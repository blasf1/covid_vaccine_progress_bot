import pandas as pd


def read(source_url: str) -> pd.DataFrame:
    return pd.read_csv(source_url, usecols=[
        "data", "doses", "pessoas_vacinadas_completamente", "pessoas_vacinadas_parcialmente", "pessoas_inoculadas"
    ])


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={
        "data": "date",
        "doses": "total_vaccinations",
        "pessoas_vacinadas_completamente": "people_fully_vaccinated",
        "pessoas_inoculadas": "people_vaccinated"
    })


def format_date(df: pd.DataFrame) -> pd.DataFrame:
    return df.assign(date=pd.to_datetime(df.date, format="%d-%m-%Y").astype(str))


def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df = df.assign(
        people_vaccinated=df.pessoas_vacinadas_parcialmente + df.people_fully_vaccinated
    )
    return df[["date", "total_vaccinations", "people_vaccinated", "people_fully_vaccinated"]]


def enrich_vaccine_name(df: pd.DataFrame) -> pd.DataFrame:
    def _enrich_vaccine_name(date: str) -> str:
        if date >= "2021-04-26":
            return "Johnson&Johnson, Moderna, Oxford/AstraZeneca, Pfizer/BioNTech"
        if date >= "2021-02-09":
            return "Moderna, Oxford/AstraZeneca, Pfizer/BioNTech"
        return "Pfizer/BioNTech"

    return df.assign(vaccine=df.date.apply(_enrich_vaccine_name))


def enrich_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.assign(
        location="Portugal",
        source_url="https://github.com/dssg-pt/covid19pt-data"
    )


def exclude_rows(df: pd.DataFrame) -> pd.DataFrame:
    # Wrong data on 2021-03-29 prevents the series from increasing monotonically
    return df[df.date < "2021-03-29"]


def sanity_checks(df: pd.DataFrame) -> pd.DataFrame:
    assert all(df.total_vaccinations.fillna(0) >= df.people_vaccinated.fillna(0))
    return df


def pipeline(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df
        .pipe(rename_columns)
        .pipe(format_date)
        #.pipe(calculate_metrics)
        .pipe(enrich_vaccine_name)
        .pipe(enrich_columns)
        .pipe(sanity_checks)
        .pipe(exclude_rows)
        .sort_values("date")
    )


def main(paths):
    source_url = "https://github.com/dssg-pt/covid19pt-data/raw/master/vacinas.csv"
    destination = paths.tmp_vax_out("Portugal")
    read(source_url).pipe(pipeline).to_csv(destination, index=False)


if __name__ == "__main__":
    main()