import pandas as pd

from vax.utils.files import export_metadata


def main(paths):

    vaccine_mapping = {
        1: "Pfizer/BioNTech",
        2: "Moderna",
        3: "Oxford/AstraZeneca",
        4: "Johnson&Johnson",
    }
    one_dose_vaccines = ["Johnson&Johnson"]

    source = (
        "https://www.data.gouv.fr/fr/datasets/r/ed648a35-a292-4664-9706-7c640265bcfa"
    )

    df = pd.read_csv(
        source, usecols=["jour", "n_cum_dose1", "n_cum_complet"], sep=";"
    )

    df = df.rename(
        columns={
            "jour": "date",
            "n_cum_dose1": "people_vaccinated",
            "n_cum_complet": "people_fully_vaccinated",
        }
    )


    df = df.assign(
        location="France",
        source_url=(
            "https://www.data.gouv.fr/fr/datasets/donnees-relatives-aux-personnes-vaccinees-contre-la-covid-19-1/"
        ),
    )

    df.to_csv(paths.tmp_vax_out("France"), index=False)


if __name__ == "__main__":
    main()
