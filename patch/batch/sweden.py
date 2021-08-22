import datetime

import pandas as pd

from cowidev.vax.utils.utils import make_monotonic
from cowidev.vax.utils.incremental import increment


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
        return daily 

    def enrich_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.assign(location=self.location, source_url=self.source_url_daily)

    def enrich_vaccine(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.assign(vaccine="Moderna, Oxford/AstraZeneca, Pfizer/BioNTech")

    def pipeline(self, df: pd.DataFrame) -> pd.DataFrame:
        return (
            df.pipe(self.enrich_vaccine).pipe(self.enrich_columns).pipe(make_monotonic)
        )


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
        df2["total_vaccinations"] = (
            df2["people_vaccinated"] + df2["people_fully_vaccinated"]
        )
        df["people_vaccinated"] = (
            df["people_vaccinated"].str.replace(r"\s", "", regex=True).astype(int)
        )
        df["people_fully_vaccinated"] = (
            df["people_fully_vaccinated"].str.replace(r"\s", "", regex=True).astype(int)
        )
        df["total_vaccinations"] = (
            df["people_vaccinated"] + df["people_fully_vaccinated"]
        )
        df = df.drop(df.loc[1:].index)
        df = df.set_index("date")
        df = df + df2
        return df

    def to_csv(self, paths):
        """Generalized."""
        df = self.read().pipe(self.pipeline)
        print(df)
        output_file = paths.tmp_vax_out("Luxembourg")
        previous_data = pd.read_csv(output_file)
        if previous_data["total_vaccinations"].iloc[-1] >= df["total_vaccinations"]:
            print("Luxembourg is up to date")
            return

        increment(
            paths=paths,
            location=df["location"],
            total_vaccinations=df["total_vaccinations"],
            people_vaccinated=df["people_vaccinated"],
            people_fully_vaccinated=df["people_fully_vaccinated"],
            date=df["date"],
            source_url=df["source_url"],
            vaccine=df["vaccine"],
        )

        #df.to_csv(paths.tmp_vax_out(self.location), index=False)


def main(paths):
    Sweden().to_csv(paths)