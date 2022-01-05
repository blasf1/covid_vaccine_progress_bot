import tempfile
import os
import json

import pandas as pd

from cowidev.vax.cmd.generate_dataset import DatasetGenerator, Bucket
from cowidev.utils import paths


def test_check_with_r():
    # Run python script
    inputs = Bucket(
        project_dir=paths.PROJECT_DIR,
        vaccinations=os.path.join(paths.SCRIPTS, "vaccinations.preliminary.csv"),
        metadata=os.path.join(paths.SCRIPTS, "metadata.preliminary.csv"),
        iso=os.path.join(paths.SCRIPTS.INPUT_ISO, "iso3166_1_alpha_3_codes.csv"),
        population=os.path.join(paths.SCRIPTS.INPUT_UN, "population_latest.csv"),
        population_sub=os.path.join(paths.SCRIPTS.INPUT_OWID, "subnational_population_2020.csv"),
        continent_countries=os.path.join(paths.SCRIPTS.INPUT_OWID, "continents.csv"),
        eu_countries=os.path.join(paths.SCRIPTS.INPUT_OWID, "eu_countries.csv"),
        income_groups=os.path.join(paths.SCRIPTS.INPUT_WB, "income_groups.csv"),
        manufacturer=os.path.join(
            paths.SCRIPTS.OUTPUT_VAX_MANUFACT,
            "*.csv",
        ),
    )
    with tempfile.TemporaryDirectory() as tmp:
        outputs = Bucket(
            locations=os.path.join(tmp, "locations.csv"),
            automated=os.path.abspath(os.path.join(tmp, "automation_state.csv")),
            vaccinations=os.path.abspath(os.path.join(tmp, "vaccinations.csv")),
            vaccinations_json=os.path.abspath(os.path.join(tmp, "vaccinations.json")),
            manufacturer=os.path.abspath(os.path.join(tmp, "vaccinations-by-manufacturer.csv")),
            grapher=os.path.abspath(os.path.join(tmp, "COVID-19 - Vaccinations.csv")),
            grapher_manufacturer=os.path.abspath(os.path.join(tmp, "COVID-19 - Vaccinations by manufacturer.csv")),
            html_table=os.path.abspath(os.path.join(tmp, "source_table.html")),
        )
        generator = DatasetGenerator(inputs, outputs)
        generator.run()

        print("\n\nTESTS BELOW\n\n")
        # Load Python generated files
        loc_p = pd.read_csv(outputs.locations)
        aut_p = pd.read_csv(outputs.automated)
        vax_p = pd.read_csv(outputs.vaccinations)
        vaxm_p = pd.read_csv(outputs.manufacturer)
        gra_p = pd.read_csv(outputs.grapher)
        gram_p = pd.read_csv(outputs.grapher_manufacturer)
        with open(outputs.vaccinations_json, "rb") as f:
            jas_p = json.load(f)
        with open(outputs.html_table, "rb") as f:
            htm_p = f.read()

        # Load R generated files
        # paths
        locations = os.path.join(paths.DATA.VACCINATIONS, "locations.csv")
        automated = os.path.abspath(os.path.join(paths.DATA.VACCINATIONS, "automation_state.csv"))
        vaccinations = os.path.abspath(os.path.join(paths.DATA.VACCINATIONS, "vaccinations.csv"))
        vaccinations_json = os.path.abspath(os.path.join(paths.DATA.VACCINATIONS, "vaccinations.json"))
        manufacturer = os.path.abspath(
            os.path.join(
                paths.DATA.VACCINATIONS,
                "vaccinations-by-manufacturer.csv",
            )
        )
        grapher = os.path.abspath(os.path.join(paths.SCRIPTS.GRAPHER, "COVID-19 - Vaccinations.csv"))
        grapher_manufacturer = os.path.abspath(
            os.path.join(
                paths.SCRIPTS.GRAPHER,
                "COVID-19 - Vaccinations by manufacturer.csv",
            )
        )
        html = os.path.abspath(os.path.join(paths.SCRIPTS.OLD, "vaccinations", "source_table.html"))
        # load
        loc_r = pd.read_csv(locations)
        aut_r = pd.read_csv(automated)
        vax_r = pd.read_csv(vaccinations)
        vaxm_r = pd.read_csv(manufacturer)
        gra_r = pd.read_csv(grapher)
        gram_r = pd.read_csv(grapher_manufacturer)
        with open(vaccinations_json, "rb") as f:
            jas_r = json.load(f)
        with open(html, "rb") as f:
            htm_r = f.read()

        # Results: Shapes
        print("----------------")
        print("Shapes")
        print("location: ", loc_r.shape, loc_p.shape)
        print("automated: ", aut_r.shape, aut_p.shape)
        print("vaccinations: ", vax_r.shape, vax_p.shape)
        print("manufacturer: ", vaxm_r.shape, vaxm_p.shape)
        print("grapher: ", gra_r.shape, gra_p.shape)
        print("grapher manufacturer: ", gram_r.shape, gram_p.shape)
        # Results: Equivalences
        print("----------------")
        print("Equals")
        print("location: ", loc_r.equals(loc_p))
        print(str((~(loc_r == loc_p)).sum()))
        print("automated: ", aut_r.equals(aut_p))
        print("vaccinations: ", vax_r.equals(vax_p))
        print("manufacturer: ", vaxm_r.equals(vaxm_p))
        print("grapher: ", gra_r.equals(gra_p))
        print("grapher manufacturer: ", gram_r.equals(gram_p))
        # Compare order of countries
        a = str(jas_r)
        b = str(jas_p).replace(".0,", ",").replace(".00,", ",").replace(".0}", "}")
        print("vaccinations_json:", jas_p == jas_r)
        print("vaccinations_json:", all([r == p for r, p in zip(jas_p, jas_r)]))
        print("vaccinations_json:", a == b)
        m = 10650  # Hardcoded, avoid comparison shift due to Denmark
        print("HTML:", htm_p[:m] == htm_r[:m])
        m = 10706
        n = 43782
        print("HTML:", htm_p[m:] == htm_r[m + 20 :])
