from datetime import date, timedelta
import datetime

import pandas as pd


def main(paths):

    date = datetime.datetime.today() - timedelta(days=1)    

    source = ("https://raw.githubusercontent.com/YorickBleijenberg/COVID_data_RIVM_Netherlands/master/vaccination/daily-dashboard-update/" 
            + date.strftime("%Y-%m-%d") 
            + "_vaccine-data.csv")

    df = pd.read_csv(
        source, usecols=["people_vaccinated", "people_fully_vaccinated", "total_estimated", "date"]
    )

    df = df.rename(
        columns={
            "total_estimated": "total_vaccinations",
        }
    )

    df = df.assign(
        location="Netherlands",
        source_url="https://github.com/YorickBleijenberg/COVID_data_RIVM_Netherlands/tree/master/vaccination/daily-dashboard-update",
    )
    df = df.pipe(enrich_vaccine_name)
    df.to_csv(paths.tmp_vax_out("Netherlands"), index=False)


# def enrich_vaccine_name(df: pd.DataFrame) -> pd.DataFrame:
#     def _enrich_vaccine_name(dt: str) -> str:
#         # See timeline in:
#         if dt < date(2021, 1, 18):
#             return "Pfizer/BioNTech"
#         elif date(2021, 1, 18) <= dt < date(2021, 2, 10):
#             return "Moderna, Pfizer/BioNTech"
#         elif date(2021, 2, 10) <= dt < date(2021, 4, 21):
#             return "Moderna, Oxford/AstraZeneca, Pfizer/BioNTech"
#         elif date(2021, 4, 21) <= dt:
#             return "Johnson&Johnson, Moderna, Oxford/AstraZeneca, Pfizer/BioNTech"

#    return df.assign(vaccine=df.date.apply(_enrich_vaccine_name))


if __name__ == "__main__":
    main()