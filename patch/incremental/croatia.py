from datetime import timedelta
import requests

import pandas as pd
import json
import undetected_chromedriver as uc
from selenium import webdriver


from vax.utils.incremental import enrich_data, increment


def read(source: str) -> pd.Series:
    source = "https://www.koronavirus.hr/json/?action=podaci_zadnji"

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--enable-webgl")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = uc.Chrome(options = options)
    driver.get(source)
    content = driver.page_source
    print("RESPONSE")
    print(content)
    data = json.loads(content)
    print(data)
    
    total_vaccinations = data[0]["CijepljenjeBrUtrosenihDoza"]
    people_vaccinated = data[0]["CijepljeniJednomDozom"]
    people_fully_vaccinated = data[0]["CijepljeniDvijeDoze"]
    date = str((pd.to_datetime(data[0]["Datum"]) - timedelta(days=1)).date())

    return pd.Series(data={
        "total_vaccinations": total_vaccinations,
        "people_vaccinated": people_vaccinated,
        "people_fully_vaccinated": people_fully_vaccinated,
        "date": date,
    })


def enrich_location(ds: pd.Series) -> pd.Series:
    return enrich_data(ds, "location", "Croatia")


def enrich_vaccine(ds: pd.Series) -> pd.Series:
    return enrich_data(ds, "vaccine", "Moderna, Oxford/AstraZeneca, Pfizer/BioNTech")


def enrich_source(ds: pd.Series) -> pd.Series:
    return enrich_data(ds, "source_url", "https://www.koronavirus.hr")


def pipeline(ds: pd.Series) -> pd.Series:
    return (
        ds
        .pipe(enrich_location)
        .pipe(enrich_vaccine)
        .pipe(enrich_source)
    )


def main(paths):
    source = "https://www.koronavirus.hr/json/?action=podaci_zadnji"
    data = read(source).pipe(pipeline)
    increment(
        paths=paths,
        location=data["location"],
        total_vaccinations=data["total_vaccinations"],
        people_vaccinated=data["people_vaccinated"],
        people_fully_vaccinated=data["people_fully_vaccinated"],
        date=data["date"],
        source_url=data["source_url"],
        vaccine=data["vaccine"]
    )


if __name__ == "__main__":
    main()