import datetime

import pandas as pd

from cowidev.vax.utils.utils import make_monotonic


class Sweden(object):
    def __init__(self):
        """Constructor."""
        self.source_url_daily = (
            "https://www.folkhalsomyndigheten.se/smittskydd-beredskap/utbrott/aktuella-utbrott/covid-19/"
            "vaccination-mot-covid-19/statistik/statistik-over-registrerade-vaccinationer-covid-19/"
        )
        self.source_url_weekly = (
            "https://fohm.maps.arcgis.com/sharing/rest/content/items/fc749115877443d29c2a49ea9eca77e9/data"
        )
        self.location = "Sweden"
        self.columns_rename = None

    def read(self) -> pd.DataFrame:
        daily = self._read_daily_data()
        print(daily)
        weekly = self._read_weekly_data()
        weekly = weekly[weekly["date"] < daily["date"].min()]
        return daily #pd.concat([daily, weekly]).sort_values("date").reset_index(drop=True)

    def enrich_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.assign(location=self.location, source_url=self.source_url_daily)

    def enrich_vaccine(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.assign(vaccine="Moderna, Oxford/AstraZeneca, Pfizer/BioNTech")

    def pipeline(self, df: pd.DataFrame) -> pd.DataFrame:
        return (
            df.pipe(self.enrich_vaccine).pipe(self.enrich_columns).pipe(make_monotonic)
        )

    def _week_to_date(self, row: int):
        origin_date = (
            pd.to_datetime("2019-12-29")
            if row.Vecka >= 52
            else pd.to_datetime("2021-01-03")
        )
        return origin_date + pd.DateOffset(days=7 * int(row.Vecka))

    def _read_weekly_data(self) -> pd.DataFrame:
        df = pd.read_excel(self.source_url_weekly, sheet_name="Vaccinerade tidsserie")
        df = df[df["Region"] == "| Sverige |"][
            ["Vecka", "Antal vaccinerade", "Vaccinationsstatus"]
        ]
        df = df.pivot_table(
            values="Antal vaccinerade", index="Vecka", columns="Vaccinationsstatus"
        ).reset_index()
        # Week-to-date logic will stop working after 2021
        if not datetime.date.today().year < 2022:
            raise ValueError("Check the year! This script is not ready for 2022!")
        df.loc[:, "date"] = df.apply(self._week_to_date, axis=1).dt.date.astype(str)
        df = (
            df.drop(columns=["Vecka"])
            .sort_values("date")
            .rename(
                columns={
                    "Minst 1 dos": "people_vaccinated",
                    "Färdigvaccinerade": "people_fully_vaccinated",
                }
            )
        )
        df.loc[:, "total_vaccinations"] = (
            df["people_vaccinated"] + df["people_fully_vaccinated"]
        )
        return df

    def _read_daily_data(self) -> pd.DataFrame:
        df = pd.read_html(self.source_url_daily)[1]
        df2 = pd.read_html(self.source_url_daily, encoding='utf-8')[2]
        
        df = df[
            [
                "Datum",
                "Antal vaccinerademed minst 1 dos*",
                "Antal vaccinerademed 2 doser",
            ]
        ].rename(
            columns={
                "Datum": "date",
                "Antal vaccinerademed minst 1 dos*": "people_vaccinated",
                "Antal vaccinerademed 2 doser": "people_fully_vaccinated",
            }
        )
        df2 = df2[
            [
                "Datum",
                "Status",
                "Antal vaccinerade födda 2003-2005",
            ]
        ].rename(
            columns={
                "Datum": "date",
                "Antal vaccinerade födda 2003-2005": "people_vaccinated",
                "Status": "status",
            }
        )
        
        aggregation_functions = {"date": "first", "people_vaccinated": "first"}
        df2 = df2.groupby(df2["status"]).aggregate(aggregation_functions)
        
        df2["people_fully_vaccinated"] = df2.loc[df2.index == "2 doser"]["people_vaccinated"]
        df2 = df2.set_index("date")
        df2 = df2.ffill().bfill()
        df2["people_vaccinated"] = (
            df2["people_vaccinated"].str.replace(r"\s", "", regex=True).astype(int)
        )
        df2["people_fully_vaccinated"] = (
            df2["people_fully_vaccinated"].str.replace(r"\s", "", regex=True).astype(int)
        )

        aggregation_functions = {"people_vaccinated": "max", "people_fully_vaccinated": "max"}
        df2 = df2.groupby(df2.index).aggregate(aggregation_functions)
        print("DF2")
        print(df2)
        df["people_vaccinated"] = (
            df["people_vaccinated"].str.replace(r"\s", "", regex=True).astype(int) + df2["people_vaccinated"]
        )
        df["people_fully_vaccinated"] = (
            df["people_fully_vaccinated"].str.replace(r"\s", "", regex=True).astype(int) + df2["people_fully_vaccinated"]
        )
        df["total_vaccinations"] = (
            df["people_vaccinated"] + df["people_fully_vaccinated"]  + df2["people_vaccinated"]+ df2["people_fully_vaccinated"]
        )
        print("DF")
        print(df)
        return df

    def to_csv(self, paths):
        """Generalized."""
        df = self.read().pipe(self.pipeline)
        print(df)
        #df.to_csv(paths.tmp_vax_out(self.location), index=False)


def main(paths):
    Sweden().to_csv(paths)