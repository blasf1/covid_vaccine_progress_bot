import os
import itertools
from datetime import datetime
from collections import ChainMap
from math import isnan
import glob
import json
import locale
from shutil import copyfile

import pandas as pd
from pandas.api.types import is_numeric_dtype

from cowidev.utils import paths
from cowidev.utils.utils import pd_series_diff_values
from cowidev.utils.clean import clean_date
from cowidev.vax.cmd.utils import get_logger
from cowidev.vax.utils.checks import VACCINES_ACCEPTED


logger = get_logger()


class Bucket(object):
    def __init__(self, **kwargs):
        self._dict = kwargs
        self.__dict__.update(kwargs)


class DatasetGenerator:
    def __init__(self, inputs, outputs):
        # Inputs
        self.inputs = inputs
        # Outputs
        self.outputs = outputs
        # Others
        self.aggregates = self.build_aggregates()
        self._countries_covered = None

    @property
    def column_names_int(self):
        return [
            "total_vaccinations",
            "people_vaccinated",
            "people_fully_vaccinated",
            "total_boosters",
            "daily_vaccinations_raw",
            "daily_vaccinations",
            "daily_vaccinations_per_million",
            "new_vaccinations_smoothed",
            "new_vaccinations_smoothed_per_million",
            "new_vaccinations",
            "new_people_vaccinated_smoothed",
        ]

    def build_aggregates(self):
        continent_countries = pd.read_csv(self.inputs.continent_countries, usecols=["Entity", "Unnamed: 3"])
        eu_countries = pd.read_csv(self.inputs.eu_countries, usecols=["Country"], squeeze=True).tolist()
        income_groups = pd.concat(
            [
                pd.read_csv(self.inputs.income_groups, usecols=["Country", "Income group"]),
                pd.read_csv(self.inputs.income_groups_compl, usecols=["Country", "Income group"]),
            ],
            ignore_index=True,
        )

        aggregates = {
            "World": {
                "excluded_locs": ["England", "Northern Ireland", "Scotland", "Wales"],
                "included_locs": None,
            },
            "European Union": {
                "excluded_locs": None,
                "included_locs": eu_countries,
            },
            "World excl. China": {
                "excluded_locs": ["China"],
                "included_locs": None,
            },
        }
        for continent in [
            "Asia",
            "Africa",
            "Europe",
            "North America",
            "Oceania",
            "South America",
        ]:
            aggregates[continent] = {
                "excluded_locs": None,
                "included_locs": (
                    continent_countries.loc[continent_countries["Unnamed: 3"] == continent, "Entity"].tolist()
                ),
            }
        for group in income_groups["Income group"].unique():
            aggregates[group] = {
                "excluded_locs": None,
                "included_locs": (income_groups.loc[income_groups["Income group"] == group, "Country"].tolist()),
            }
        return aggregates

    def pipeline_automated(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate DataFrame for automated states."""
        return df.sort_values(by=["automated", "location"], ascending=[False, True])[
            ["location", "automated"]
        ].reset_index(drop=True)

    def pipeline_locations(
        self, df_vax: pd.DataFrame, df_metadata: pd.DataFrame, df_iso: pd.DataFrame
    ) -> pd.DataFrame:
        """Generate DataFrame for locations."""

        def _pretty_vaccine(vaccines):
            return ", ".join(sorted(v.strip() for v in vaccines.split(",")))

        df_vax = (
            df_vax.sort_values(by=["location", "date"])
            .drop_duplicates(subset=["location"], keep="last")
            .rename(
                columns={
                    "date": "last_observation_date",
                    "source_url": "source_website",
                }
            )
        )

        if len(df_metadata) != len(df_vax):
            loc_miss = pd_series_diff_values(df_metadata.location, df_vax.location)
            a = df_metadata[df_metadata.location.isin(loc_miss)]
            b = df_vax[df_vax.location.isin(loc_miss)]
            print("metadata\n", a)
            print("data\n", b)
            raise ValueError(f"Missmatch between vaccination data and metadata! Unknown location {loc_miss}.")

        return (
            df_vax.assign(vaccines=df_vax.vaccine.apply(_pretty_vaccine))  # Keep only last vaccine set
            .merge(df_metadata, on="location")
            .merge(df_iso, on="location")
        )[
            [
                "location",
                "iso_code",
                "vaccines",
                "last_observation_date",
                "source_name",
                "source_website",
            ]
        ]

    def _get_aggregate(self, df, agg_name, included_locs, excluded_locs):
        # Take rows that matter
        agg = df[~df.location.isin(self.aggregates.keys())]  # remove aggregated rows
        if excluded_locs is not None:
            agg = agg[~agg.location.isin(excluded_locs)]
        elif included_locs is not None:
            agg = agg[agg.location.isin(included_locs)]

        # Get full location-date grid
        agg = (
            pd.DataFrame(
                itertools.product(agg.location.unique(), agg.date.unique()),
                columns=[agg.location.name, agg.date.name],
            )
            .merge(agg, on=["date", "location"], how="outer")
            .sort_values(by=["location", "date"])
        )

        # NaN: Forward filling + Zero-filling if all metric is NaN
        cols = [
            "total_vaccinations",
            "people_vaccinated",
            "people_fully_vaccinated",
            "total_boosters",
        ]
        grouper = agg.groupby("location")
        for col in cols:
            agg[col] = grouper[col].apply(lambda x: x.fillna(0) if x.isnull().all() else x.fillna(method="ffill"))

        # Aggregate
        agg = agg.groupby("date").sum().reset_index().assign(location=agg_name)
        agg = agg[agg.date.dt.date < datetime.now().date()]
        return agg

    def pipe_aggregates(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info(f"Building aggregate regions {list(self.aggregates.keys())}")
        aggs = []
        for agg_name, _ in self.aggregates.items():
            aggs.append(
                self._get_aggregate(
                    df=df,
                    agg_name=agg_name,
                    included_locs=self.aggregates[agg_name]["included_locs"],
                    excluded_locs=self.aggregates[agg_name]["excluded_locs"],
                )
            )
        return pd.concat([df] + aggs, ignore_index=True)

    def pipe_daily(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Adding daily metrics")
        df = df.sort_values(by=["location", "date"])
        df = df.assign(new_vaccinations=df.groupby("location").total_vaccinations.diff())
        df.loc[df.date.diff().dt.days > 1, "new_vaccinations"] = None
        df = df.sort_values(["location", "date"])
        return df

    def _add_smoothed(self, df: pd.DataFrame) -> pd.DataFrame:
        # NEW VACCINATIONS
        # Range where total_vaccinations is registered
        dt_min = df.dropna(subset=["total_vaccinations"]).date.min()
        dt_max = df.dropna(subset=["total_vaccinations"]).date.max()
        df_nan = df[(df.date < dt_min) | (df.date > dt_max)]

        # Add missing dates
        df = df.merge(
            pd.Series(pd.date_range(dt_min, dt_max), name="date"),
            how="right",
        ).sort_values(by="date")

        # Calculate and add smoothed vars
        df["new_vaccinations_smoothed"] = (
            df.total_vaccinations.interpolate(method="linear")
            .diff()
            .rolling(7, min_periods=1)
            .mean()
            .apply(lambda x: round(x) if not isnan(x) else x)
        )

        # Add missing dates
        df = pd.concat([df, df_nan], ignore_index=True).sort_values("date")
        df.loc[:, "location"] = df.location.dropna().iloc[0]

        # PEOPLE_VACCINATED
        # Range where people_vaccinated is registered
        dt_min = df.dropna(subset=["people_vaccinated"]).date.min()
        dt_max = df.dropna(subset=["people_vaccinated"]).date.max()
        df_nan = df[(df.date < dt_min) | (df.date > dt_max)]

        # Add missing dates
        df = df.merge(
            pd.Series(pd.date_range(dt_min, dt_max), name="date"),
            how="right",
        ).sort_values(by="date")

        # Calculate and add smoothed vars
        df["new_people_vaccinated_smoothed"] = (
            df.people_vaccinated.interpolate(method="linear")
            .diff()
            .rolling(7, min_periods=1)
            .mean()
            .apply(lambda x: round(x) if not isnan(x) else x)
        )

        # Add missing dates
        df = pd.concat([df, df_nan], ignore_index=True).sort_values("date")
        df.loc[:, "location"] = df.location.dropna().iloc[0]
        return df

    def pipe_smoothed(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Adding smoothed variables")
        return df.groupby("location").apply(self._add_smoothed).reset_index(drop=True)

    def get_population(self, df_subnational: pd.DataFrame) -> pd.DataFrame:
        # Build population dataframe
        column_rename = {"entity": "location", "population": "population"}
        pop = pd.read_csv(self.inputs.population, usecols=column_rename.keys()).rename(columns=column_rename)
        pop = pd.concat([pop, df_subnational], ignore_index=True)

        # The US population denominator is more complex to calculate, as the US CDC is pulling
        # together data from multiple territories and federal agencies to build national figures.
        # To ensure that we use the correct territorial boundaries in the denominator, we use the
        # population figure provided by the CDC in its data.
        pop.loc[pop.location == "United States", "population"] = 332008832

        return pop

    def pipe_capita(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Adding per-capita variables")
        # Get data
        df_subnational = pd.read_csv(self.inputs.population_sub, usecols=["location", "population"])
        pop = self.get_population(df_subnational)
        df = df.merge(pop, on="location", validate="many_to_one", how="left")
        if df.population.isna().any():
            missing_locs = df[df.population.isna()].location.unique()
            raise ValueError(f"Missing population data for {missing_locs}")

        # Get covered countries
        locations = df.location.unique()
        ncountries = df_subnational.location.tolist() + list(self.aggregates.keys())
        self._countries_covered = list(filter(lambda x: x not in ncountries, locations))
        # Obtain per-capita metrics
        df = df.assign(
            total_vaccinations_per_hundred=(df.total_vaccinations * 100 / df.population).round(2),
            people_vaccinated_per_hundred=(df.people_vaccinated * 100 / df.population).round(2),
            people_fully_vaccinated_per_hundred=(df.people_fully_vaccinated * 100 / df.population).round(2),
            total_boosters_per_hundred=(df.total_boosters * 100 / df.population).round(2),
            new_vaccinations_smoothed_per_million=(df.new_vaccinations_smoothed * 1000000 / df.population).round(),
            new_people_vaccinated_smoothed_per_hundred=(df.new_people_vaccinated_smoothed * 100 / df.population).round(
                3
            ),
        )
        df.loc[:, "people_fully_vaccinated"] = df.people_fully_vaccinated.replace({0: pd.NA})
        df.loc[df.people_fully_vaccinated.isnull(), "people_fully_vaccinated_per_hundred"] = pd.NA
        df.loc[:, "total_boosters"] = df.total_boosters.replace({0: pd.NA})
        df.loc[df.total_boosters.isnull(), "total_boosters_per_hundred"] = pd.NA
        df["people_unvaccinated"] = df.population - df.people_vaccinated
        df.loc[df.people_unvaccinated < 0, "people_unvaccinated"] = 0
        return df.drop(columns=["population"])

    def pipe_vax_checks(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Sanity checks")
        # Config
        skip_countries = ["Pitcairn"]
        # Sanity checks
        df_to_check = df[-df.location.isin(skip_countries)]
        if not (df_to_check.total_vaccinations.dropna() >= 0).all():
            raise ValueError("Negative values found! Check values in `total_vaccinations`.")
        if not (df_to_check.new_vaccinations_smoothed.dropna() >= 0).all():
            raise ValueError("Negative values found! Check values in `new_vaccinations_smoothed`.")
        if not (df_to_check.new_vaccinations_smoothed_per_million.dropna() <= 120000).all():
            raise ValueError(" Huge values found! Check values in `new_vaccinations_smoothed_per_million`.")
        return df

    def pipe_to_int(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Converting INT columns to int")
        # Ensure Int types
        cols = df.columns
        count_cols = [col for col in self.column_names_int if col in cols]
        df[count_cols] = df[count_cols].astype("Int64").fillna(pd.NA)
        return df

    def pipeline_vaccinations(self, df: pd.DataFrame) -> pd.DataFrame:
        return (
            df[
                [
                    "date",
                    "location",
                    "total_vaccinations",
                    "people_vaccinated",
                    "people_fully_vaccinated",
                    "total_boosters",
                ]
            ]
            .pipe(self.pipe_aggregates)
            .pipe(self.pipe_daily)
            .pipe(self.pipe_smoothed)
            .pipe(self.pipe_capita)
            .pipe(self.pipe_vax_checks)
            .pipe(self.pipe_to_int)
            .sort_values(by=["location", "date"])
        )

    def pipe_vaccinations_csv(self, df: pd.DataFrame, df_iso: pd.DataFrame) -> pd.DataFrame:
        return df.merge(df_iso, on="location").rename(
            columns={
                "new_vaccinations_smoothed": "daily_vaccinations",
                "new_vaccinations_smoothed_per_million": "daily_vaccinations_per_million",
                "new_vaccinations": "daily_vaccinations_raw",
                "new_people_vaccinated_smoothed": "daily_people_vaccinated",
                "new_people_vaccinated_smoothed_per_hundred": "daily_people_vaccinated_per_hundred",
            }
        )[
            [
                "location",
                "iso_code",
                "date",
                "total_vaccinations",
                "people_vaccinated",
                "people_fully_vaccinated",
                "total_boosters",
                "daily_vaccinations_raw",
                "daily_vaccinations",
                "total_vaccinations_per_hundred",
                "people_vaccinated_per_hundred",
                "people_fully_vaccinated_per_hundred",
                "total_boosters_per_hundred",
                "daily_vaccinations_per_million",
                "daily_people_vaccinated",
                "daily_people_vaccinated_per_hundred",
            ]
        ]

    def pipe_vaccinations_json(self, df: pd.DataFrame) -> list:
        location_iso_codes = df[["location", "iso_code"]].drop_duplicates().values.tolist()
        metrics = [column for column in df.columns if column not in {"location", "iso_code"}]
        df = df.assign(date=df.date.apply(clean_date))
        return [
            {
                "country": location,
                "iso_code": iso_code,
                "data": [
                    {**x[i]}
                    for i, x in df.loc[(df.location == location) & (df.iso_code == iso_code), metrics]
                    .stack()
                    .groupby(level=0)
                ],
            }
            for location, iso_code in location_iso_codes
        ]

    def pipe_manufacturer_select_cols(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[
            [
                "location",
                "date",
                "vaccine",
                "total_vaccinations",
            ]
        ].sort_values(["location", "date", "vaccine"])

    def pipe_manufacturer_add_eu(self, df: pd.DataFrame) -> pd.DataFrame:
        eu_countries = pd.read_csv(self.inputs.eu_countries, usecols=["Country"], squeeze=True).tolist()
        eu_manufacturer = (
            df[df.location.isin(eu_countries)]
            .pivot(index=["location", "vaccine"], columns="date", values="total_vaccinations")
            .reset_index()
            .melt(id_vars=["location", "vaccine"], var_name="date", value_name="total_vaccinations")
            .sort_values("date")
        )
        eu_manufacturer["total_vaccinations"] = (
            eu_manufacturer.groupby(["location", "vaccine"]).ffill().total_vaccinations
        )
        eu_manufacturer = (
            eu_manufacturer[eu_manufacturer.date.astype(str) >= "2020-12-27"]
            .groupby(["date", "vaccine"], as_index=False)
            .sum()
            .assign(location="European Union")
        )
        return pd.concat([df, eu_manufacturer])

    def pipe_manufacturer_filter_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[df.date.astype(str) >= "2020-12-01"]

    def pipe_manufacturer_checks(self, df: pd.DataFrame) -> pd.DataFrame:
        vaccines_wrong = set(df.vaccine).difference(VACCINES_ACCEPTED)
        if vaccines_wrong:
            raise ValueError(f"Invalid vaccines found in manufacturer file! {vaccines_wrong}")
        return df

    def pipeline_manufacturer(self, df: pd.DataFrame) -> pd.DataFrame:
        return (
            df.pipe(self.pipe_manufacturer_select_cols)
            .pipe(self.pipe_manufacturer_add_eu)
            .pipe(self.pipe_manufacturer_filter_dates)
            .pipe(self.pipe_manufacturer_checks)
            .pipe(self.pipe_to_int)
        )

    def pipe_age_checks(self, df: pd.DataFrame) -> pd.DataFrame:
        if df[["location", "date", "age_group_min"]].isnull().sum().sum() != 0:
            raise ValueError(
                "Unexpected NaN values found in one (or several) fields from `location`, `date`, `age_group_min`"
            )
        if not (
            is_numeric_dtype(df.people_vaccinated_per_hundred)
            and is_numeric_dtype(df.people_fully_vaccinated_per_hundred)
            and is_numeric_dtype(df.people_with_booster_per_hundred)
        ):
            raise TypeError("Metrics should be numeric! E.g., 50.23")
        return df

    def pipe_metrics_format(self, df: pd.DataFrame) -> pd.DataFrame:
        cols_metrics = [
            "people_vaccinated_per_hundred",
            "people_fully_vaccinated_per_hundred",
            "people_with_booster_per_hundred",
        ]
        df[cols_metrics] = df[cols_metrics].round(2)
        return df

    def pipe_age_group(self, df: pd.DataFrame) -> pd.DataFrame:
        # Get age group
        age_min = df.age_group_min.astype(str)
        age_max = df.age_group_max.astype("Int64").apply(lambda x: str(x) if not pd.isna(x) else "+")
        age_group = (age_min + "-" + age_max).replace(to_replace=r"-\+", value="+", regex=True)
        return df.assign(age_group=age_group)

    def pipe_age_output(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.dropna(
            subset=[
                "people_vaccinated_per_hundred",
                "people_fully_vaccinated_per_hundred",
                "people_with_booster_per_hundred",
            ],
            how="all",
        )[
            [
                "location",
                "date",
                "age_group",
                "people_vaccinated_per_hundred",
                "people_fully_vaccinated_per_hundred",
                "people_with_booster_per_hundred",
            ]
        ].sort_values(
            ["location", "date", "age_group"]
        )

    def pipeline_age(self, df: pd.DataFrame) -> pd.DataFrame:
        return (
            df.pipe(self.pipe_age_checks)
            .pipe(self.pipe_metrics_format)
            .pipe(self.pipe_age_group)
            .pipe(self.pipe_age_output)
        )

    def add_booster_share(self, df: pd.DataFrame) -> pd.DataFrame:
        shape_before = df.shape
        global_boosters = df[df.location == "World"][
            ["location", "date", "total_vaccinations", "total_boosters"]
        ].sort_values("date")
        global_boosters[["total_vaccinations", "total_boosters"]] = global_boosters[
            ["total_vaccinations", "total_boosters"]
        ].astype(float)
        global_boosters["share_of_boosters"] = (
            (
                (global_boosters.total_boosters - global_boosters.total_boosters.shift(1))
                / (global_boosters.total_vaccinations - global_boosters.total_vaccinations.shift(1))
            )
            .rolling(14)
            .mean()
            .round(4)
        )
        global_boosters = global_boosters.drop(columns=["total_vaccinations", "total_boosters"])
        df = pd.merge(df, global_boosters, how="left", on=["location", "date"], validate="one_to_one")
        assert (
            df.shape[0] == shape_before[0] and df.shape[1] == shape_before[1] + 1
        ), "Adding share_of_boosters has changed the shape of the dataframe in an unintended way!"
        return df

    def pipe_grapher(
        self,
        df: pd.DataFrame,
        date_ref: datetime = datetime(2020, 1, 21),
        fillna: bool = False,
        fillna_0: bool = True,
    ) -> pd.DataFrame:
        df = (
            df.rename(
                columns={
                    "date": "Year",
                    "location": "Country",
                }
            ).assign(Year=(df.date - date_ref).dt.days)
        ).copy()
        columns_first = ["Country", "Year"]
        columns_rest = [col for col in df.columns if col not in columns_first]
        col_order = columns_first + columns_rest
        df = df[col_order].sort_values(["Country", "Year"])
        if fillna:
            filled = df.groupby(["Country"])[columns_rest].fillna(method="ffill")
            if fillna_0:
                df[columns_rest] = filled.fillna(0)
            else:
                df[columns_rest] = filled
        return df

    def pipe_manufacturer_pivot(self, df: pd.DataFrame) -> pd.DataFrame:
        x = df.groupby(["location", "date", "vaccine"]).count().sort_values("total_vaccinations")
        mask = x.total_vaccinations != 1
        if mask.sum() != 0:
            raise ValueError(f"Check entries {x[mask]}")
        return df.pivot(index=["location", "date"], columns="vaccine", values="total_vaccinations").reset_index()

    def pipeline_manufacturer_grapher(self, df: pd.DataFrame) -> pd.DataFrame:
        return (
            df.pipe(self.pipe_manufacturer_pivot)
            .pipe(self.pipe_grapher, date_ref=datetime(2021, 1, 1), fillna=True)
            .pipe(self.pipe_to_int)
        )

    def pipe_age_pivot(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.pivot(
            index=["location", "date"],
            columns="age_group",
        ).reset_index()
        # Ensure column order
        columns = pd.MultiIndex.from_tuples(sorted(df.columns, key=lambda x: x[0] + x[1]))
        df = df[columns]
        columns_wrong_1 = df.people_vaccinated_per_hundred.columns.difference(
            df.people_fully_vaccinated_per_hundred.columns
        )
        columns_wrong_2 = df.people_fully_vaccinated_per_hundred.columns.difference(
            df.people_with_booster_per_hundred.columns
        )
        if columns_wrong_1.any() or columns_wrong_2.any():
            raise ValueError(f"There is missmatch between age groups in people vaccinated and people fully vaccinated")
        return df

    def pipe_age_partly(self, df: pd.DataFrame) -> pd.DataFrame:
        # Add partly vaccinated
        y = (df["people_vaccinated_per_hundred"] - df["people_fully_vaccinated_per_hundred"]).round(2)
        cols = pd.MultiIndex.from_tuples([("people_partly_vaccinated_per_hundred", yy) for yy in y.columns])
        y.columns = cols
        df[cols] = y
        return df

    def pipe_age_flatten(self, df: pd.DataFrame) -> pd.DataFrame:
        # Flatten columns
        new_cols = []
        for col in df.columns:
            if col[0] == "people_vaccinated_per_hundred":
                new_cols.append(f"{col[1]}_start")
            elif col[0] == "people_fully_vaccinated_per_hundred":
                new_cols.append(f"{col[1]}_fully")
            elif col[0] == "people_partly_vaccinated_per_hundred":
                new_cols.append(f"{col[1]}_partly")
            elif col[0] == "people_with_booster_per_hundred":
                new_cols.append(f"{col[1]}_booster")
            else:
                new_cols.append(col[0])
        df.columns = new_cols
        return df

    def pipeline_age_grapher(self, df: pd.DataFrame) -> pd.DataFrame:
        return (
            df.pipe(self.pipe_age_pivot)
            .pipe(self.pipe_age_partly)
            .pipe(self.pipe_age_flatten)
            .pipe(
                self.pipe_grapher,
                date_ref=datetime(2021, 1, 1),
                fillna=True,
                fillna_0=False,
            )
        )

    def pipe_locations_to_html(self, df: pd.DataFrame) -> pd.DataFrame:
        locale.setlocale(locale.LC_TIME, "en_US")
        # build table
        country_faqs = {
            "Israel",
            "Palestine",
        }
        faq = ' (see <a href="https://ourworldindata.org/covid-vaccinations#frequently-asked-questions">FAQ</a>)'
        df = df.assign(
            location=(df.location.apply(lambda x: f"<td><strong>{x}</strong>{faq if x in country_faqs else ''}</td>")),
            source=('<td><a href="' + df.source_website + '">' + df.source_name + "</a></td>"),
            last_observation_date=(df.last_observation_date.apply(lambda x: f"<td>{x.strftime('%b. %e, %Y')}</td>")),
            vaccines=(df.vaccines.apply(lambda x: f"<td>{x}</td>")),
        )[["location", "source", "last_observation_date", "vaccines"]]
        df.columns = [col.capitalize().replace("_", " ") for col in df.columns]
        body = ("<tr>" + df.sum(axis=1) + "</tr>").sum(axis=0)
        header = "<tr>" + "".join(f"<th>{col}</th>" for col in df.columns) + "</tr>"
        html_table = f"<table><tbody>{header}{body}</tbody></table>"
        coverage_info = f"Vaccination against COVID-19 has now started in {len(self._countries_covered)} locations."
        html_table = (
            f'<div class="wp-block-full-content-width"><p><strong>{coverage_info}</strong></p>{html_table}</div>\n'
        ).replace("  ", " ")
        return html_table

    def export(
        self,
        df_automated: pd.DataFrame,
        df_locations: pd.DataFrame,
        df_vaccinations: pd.DataFrame,
        df_manufacturer: pd.DataFrame,
        df_age: pd.DataFrame,
        json_vaccinations: dict,
        df_grapher: pd.DataFrame,
        df_manufacturer_grapher: pd.DataFrame,
        df_age_grapher: pd.DataFrame,
        html_table: str,
    ):
        # Export
        files = [
            (df_automated, self.outputs.automated),
            (df_locations, self.outputs.locations),
            (df_vaccinations, self.outputs.vaccinations),
            (df_manufacturer, self.outputs.manufacturer),
            (df_age, self.outputs.age),
            (json_vaccinations, self.outputs.vaccinations_json),
            (df_grapher, self.outputs.grapher),
            (df_manufacturer_grapher, self.outputs.grapher_manufacturer),
            (df_age_grapher, self.outputs.grapher_age),
            (html_table, self.outputs.html_table),
        ]
        for obj, path in files:
            if path.endswith(".csv"):
                obj.to_csv(path, index=False)
            elif path.endswith(".json"):
                with open(path, "w") as f:
                    json.dump(obj, f, indent=2)  # default=lambda o: o.__dict__, sort_keys=True
            elif path.endswith(".html"):
                with open(path, "w") as f:
                    f.write(obj)
            else:
                raise ValueError("Format not supported. Currently only csv, json and html are accepted!")

    def _cp_locations_files(self):
        copyfile(paths.SCRIPTS.OUTPUT_VAX_META_MANUFACT, paths.DATA.VAX_META_MANUFACT)
        copyfile(paths.SCRIPTS.OUTPUT_VAX_META_AGE, paths.DATA.VAX_META_AGE)

    def run(self):
        print("-- Generating dataset... --")
        logger.info("1/10 Loading input data...")
        try:
            df_metadata = pd.read_csv(self.inputs.metadata)
            df_vaccinations = pd.read_csv(self.inputs.vaccinations, parse_dates=["date"])
        except FileNotFoundError:
            raise FileNotFoundError(
                "Internal files not found! Make sure to run `proccess-data` step prior to running `generate-dataset`."
            )
        df_iso = pd.read_csv(self.inputs.iso)
        files_manufacturer = glob.glob(self.inputs.manufacturer)
        df_manufacturer = pd.concat(
            (pd.read_csv(filepath, parse_dates=["date"]) for filepath in files_manufacturer),
            ignore_index=True,
        )
        files_age = glob.glob(self.inputs.age)
        df_age = pd.concat(
            (pd.read_csv(filepath, parse_dates=["date"]) for filepath in files_age),
            ignore_index=True,
        )

        # Metadata
        logger.info("2/10 Generating `automated_state` table...")
        df_automated = df_metadata.pipe(self.pipeline_automated)  # Export to AUTOMATED_STATE_FILE
        logger.info("3/10 Generating `locations` table...")
        df_locations = df_vaccinations.pipe(self.pipeline_locations, df_metadata, df_iso)  # Export to LOCATIONS_FILE

        # Vaccinations
        logger.info("4/10 Generating `vaccinations` table...")
        df_vaccinations_base = df_vaccinations.pipe(self.pipeline_vaccinations)
        df_vaccinations = df_vaccinations_base.pipe(self.pipe_vaccinations_csv, df_iso)
        logger.info("5/10 Generating `vaccinations` json...")
        json_vaccinations = df_vaccinations.pipe(self.pipe_vaccinations_json)

        # Manufacturer
        logger.info("6/10 Generating `manufacturer` table...")
        df_manufacturer = df_manufacturer.pipe(self.pipeline_manufacturer)

        # Age
        logger.info("7/10 Generating `age` table...")
        df_age = df_age.pipe(self.pipeline_age)

        # Grapher
        logger.info("8/10 Generating `grapher` tables...")
        df_grapher = df_vaccinations_base.pipe(self.add_booster_share).pipe(self.pipe_grapher)
        df_manufacturer_grapher = df_manufacturer.pipe(self.pipeline_manufacturer_grapher)
        df_age_grapher = df_age.pipe(self.pipeline_age_grapher)
        # df_age_grapher_fully = df_age.pipe(self.pipeline_age_grapher, "people_fully_vaccinated_per_hundred")

        # HTML
        logger.info("9/10 Generating HTML...")
        html_table = df_locations.pipe(self.pipe_locations_to_html)

        # Export
        logger.info("10/10 Exporting files...")
        self.export(
            df_automated=df_automated,
            df_locations=df_locations,
            df_vaccinations=df_vaccinations,
            df_manufacturer=df_manufacturer,
            df_age=df_age,
            json_vaccinations=json_vaccinations,
            df_grapher=df_grapher,
            df_manufacturer_grapher=df_manufacturer_grapher,
            df_age_grapher=df_age_grapher,
            html_table=html_table,
        )
        self._cp_locations_files()


def main_generate_dataset():
    # Select columns
    # TODO: Paths might better defined in vax.utils.paths.Paths
    inputs = Bucket(
        project_dir=paths.PROJECT_DIR,
        vaccinations=os.path.join(str(paths.SCRIPTS), "vaccinations.preliminary.csv"),
        metadata=os.path.join(str(paths.SCRIPTS), "metadata.preliminary.csv"),
        iso=os.path.join(paths.SCRIPTS.INPUT_ISO, "iso3166_1_alpha_3_codes.csv"),
        population=os.path.join(paths.SCRIPTS.INPUT_UN, "population_latest.csv"),
        population_sub=os.path.join(paths.SCRIPTS.INPUT_OWID, "subnational_population_2020.csv"),
        continent_countries=os.path.join(paths.SCRIPTS.INPUT_OWID, "continents.csv"),
        eu_countries=os.path.join(paths.SCRIPTS.INPUT_OWID, "eu_countries.csv"),
        income_groups=os.path.join(paths.SCRIPTS.INPUT_WB, "income_groups.csv"),
        income_groups_compl=os.path.join(paths.SCRIPTS.INPUT_OWID, "income_groups_complement.csv"),
        manufacturer=os.path.join(
            paths.SCRIPTS.OUTPUT_VAX_MANUFACT,
            "*.csv",
        ),
        age=os.path.join(paths.SCRIPTS.OUTPUT_VAX_AGE, "*.csv"),
    )
    outputs = Bucket(
        locations=os.path.join(paths.DATA.VACCINATIONS, "locations.csv"),
        automated=os.path.abspath(os.path.join(paths.SCRIPTS.OUTPUT_VAX, "automation_state.csv")),
        vaccinations=os.path.abspath(os.path.join(paths.DATA.VACCINATIONS, "vaccinations.csv")),
        vaccinations_json=(os.path.abspath(os.path.join(paths.DATA.VACCINATIONS, "vaccinations.json"))),
        manufacturer=(
            os.path.abspath(
                os.path.join(
                    paths.DATA.VACCINATIONS,
                    "vaccinations-by-manufacturer.csv",
                )
            )
        ),
        age=(
            os.path.abspath(
                os.path.join(
                    paths.DATA.VACCINATIONS,
                    "vaccinations-by-age-group.csv",
                )
            )
        ),
        grapher=os.path.abspath(os.path.join(paths.SCRIPTS.GRAPHER, "COVID-19 - Vaccinations.csv")),
        grapher_manufacturer=os.path.abspath(
            os.path.join(
                paths.SCRIPTS.GRAPHER,
                "COVID-19 - Vaccinations by manufacturer.csv",
            )
        ),
        grapher_age=os.path.abspath(
            os.path.join(
                paths.SCRIPTS.GRAPHER,
                "COVID-19 - Vaccinations by age group.csv",
            )
        ),
        html_table=os.path.abspath(os.path.join(paths.SCRIPTS.OUTPUT_VAX, "source_table.html")),
    )
    generator = DatasetGenerator(inputs, outputs)
    generator.run()

    # Export timestamp
    timestamp_filename = os.path.join(paths.DATA.TIMESTAMP, "owid-covid-data-last-updated-timestamp-vaccination.txt")
    with open(timestamp_filename, "w") as timestamp_file:
        timestamp_file.write(datetime.utcnow().replace(microsecond=0).isoformat())
