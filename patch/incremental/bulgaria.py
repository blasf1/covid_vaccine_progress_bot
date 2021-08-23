import re

import requests
import pandas as pd
from bs4 import BeautifulSoup

from cowidev.vax.utils.incremental import enrich_data, increment
from cowidev.vax.utils.dates import localdate


def read(source: str) -> pd.Series:
    soup = BeautifulSoup(requests.get(source).content, "html.parser")
    return parse_data(soup)


def parse_data(soup: BeautifulSoup) -> pd.Series:
    table = soup.find("p", string=re.compile("Поставени ваксини по")).parent.find(
        "table"
    )
    data = pd.read_html(str(table))[0]
    data = data.droplevel(level=0, axis=1)
    data = data[data["Област"] == "Общо"]
    return data.set_index(data.columns[0]).T.squeeze()


def enrich_date(ds: pd.Series) -> pd.Series:
    date = localdate("Europe/Sofia")
    return enrich_data(ds, "date", date)


def translate_index(ds: pd.Series) -> pd.Series:
    return ds.rename(
        {
            "Общ брой лица със завършен ваксинационен цикъл": "people_fully_vaccinated",
            "Общо поставени дози": "total_vaccinations",
        }
    )


def add_totals(ds: pd.Series) -> pd.Series:
    people_vaccinated = int(ds["total_vaccinations"]) - int(
        ds["people_fully_vaccinated"]
    )
    return enrich_data(ds, "people_vaccinated", people_vaccinated)


def enrich_location(ds: pd.Series) -> pd.Series:
    return enrich_data(ds, "location", "Bulgaria")


def enrich_vaccine(ds: pd.Series) -> pd.Series:
    return enrich_data(
        ds, "vaccine", "Johnson&Johnson, Oxford/AstraZeneca, Moderna, Pfizer/BioNTech"
    )


def enrich_source(ds: pd.Series) -> pd.Series:
    return enrich_data(ds, "source_url", "https://coronavirus.bg/bg/statistika")


def pipeline(ds: pd.Series) -> pd.Series:
    return (
        ds.pipe(translate_index)
        .pipe(add_totals)
        .pipe(enrich_date)
        .pipe(enrich_location)
        .pipe(enrich_vaccine)
        .pipe(enrich_source)
    )


def main(paths):
    source = "https://coronavirus.bg/bg/statistika"
    data = read(source).pipe(pipeline)
    increment(
        paths=paths,
        location=data["location"],
        total_vaccinations=int(data["total_vaccinations"]),
        people_vaccinated=int(data["people_vaccinated"]),
        people_fully_vaccinated=int(data["people_fully_vaccinated"]),
        date=data["date"],
        source_url=data["source_url"],
        vaccine=data["vaccine"],
    )


if __name__ == "__main__":
    main()
