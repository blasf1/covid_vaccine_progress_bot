import re

import pandas as pd

from vax.utils.incremental import enrich_data, increment, clean_count
from vax.utils.utils import get_soup
from vax.utils.dates import localdate


def read(source: str) -> pd.Series:
    soup = get_soup(source)

    for label in soup.find_all(class_="number-label"):
        if label.text == "Total vaccins administrés":
            container = label.parent.parent

    date = soup.find(text=" Prochaine mise à jour: ").find_next_sibling("strong")
    print("The date for luxembourg is " + date.text)

    return pd.Series(
        data={
            "total_vaccinations": parse_total_vaccinations(container),
            "people_vaccinated": parse_people_vaccinated(container),
            "people_fully_vaccinated": parse_people_fully_vaccinated(container),
            "source_url": source,
        }
    )


def parse_total_vaccinations(container) -> int:
    total_vaccinations = clean_count(container.find(class_="number").text)
    return total_vaccinations


def parse_people_vaccinated(container) -> int:
    people_vaccinated = container.find(class_="cmp-text").text
    people_vaccinated = re.search(r"Dose 1\:\s([\d\. ]{6,})", people_vaccinated).group(
        1
    )
    people_vaccinated = clean_count(people_vaccinated)
    return people_vaccinated


def parse_people_fully_vaccinated(container) -> int:
    people_fully_vaccinated = container.find(class_="cmp-text").text
    people_fully_vaccinated = re.search(
        r"Dose 2\:\s([\d\. ]{6,})", people_fully_vaccinated
    ).group(1)
    people_fully_vaccinated = clean_count(people_fully_vaccinated)
    return people_fully_vaccinated


def enrich_date(ds: pd.Series) -> pd.Series:
    return enrich_data(ds, "date", localdate("Europe/Luxembourg"))


def enrich_location(ds: pd.Series) -> pd.Series:
    return enrich_data(ds, "location", "Luxembourg")


def enrich_vaccine(ds: pd.Series) -> pd.Series:
    return enrich_data(ds, "vaccine", "Moderna, Oxford/AstraZeneca, Pfizer/BioNTech")


def pipeline(ds: pd.Series) -> pd.Series:
    return ds.pipe(enrich_date).pipe(enrich_location).pipe(enrich_vaccine)


def main(paths):
    source = "https://covid19.public.lu/fr.html"
    data = read(source).pipe(pipeline)
    increment(
        paths=paths,
        location=data["location"],
        total_vaccinations=data["total_vaccinations"],
        people_vaccinated=data["people_vaccinated"],
        people_fully_vaccinated=data["people_fully_vaccinated"],
        date=data["date"],
        source_url=data["source_url"],
        vaccine=data["vaccine"],
    )


if __name__ == "__main__":
    main()