import os

import pandas as pd

from cowidev.vax.utils.gsheets import VaccinationGSheet
from cowidev.vax.process import process_location
from cowidev.vax.cmd.utils import get_logger, print_eoe
from pandas.core.base import DataError
from pandas.errors import ParserError
from cowidev.utils import paths


logger = get_logger()


def read_csv(filepath):
    try:
        return pd.read_csv(filepath)
    except:
        raise ParserError(f"Error tokenizing data from file {filepath}")


def main_process_data(
    gsheets_api,
    google_spreadsheet_vax_id: str,
    skip_complete: list = None,
    skip_monotonic: dict = {},
    skip_anomaly: dict = {},
):
    print("-- Processing data... --")
    # Get data from sheets
    logger.info("Getting data from Google Spreadsheet...")
    gsheet = VaccinationGSheet(gsheets_api, google_spreadsheet_vax_id)
    df_manual_list = gsheet.df_list()

    # Get automated-country data
    logger.info("Getting data from output...")
    automated = gsheet.automated_countries
    filepaths_auto = [paths.out_vax(country) for country in automated]
    df_auto_list = [read_csv(filepath) for filepath in filepaths_auto]

    # Concatenate
    vax = df_manual_list + df_auto_list

    # Check that no location is present in both manual and automated data
    manual_locations = set([df.location[0] for df in df_manual_list])
    auto_locations = os.listdir(paths.SCRIPTS.OUTPUT_VAX_MAIN)
    auto_locations = set([loc.replace(".csv", "") for loc in auto_locations])
    common_locations = auto_locations.intersection(manual_locations)
    if len(common_locations) > 0:
        raise DataError(f"The following locations have data in both output/main_data and GSheet: {common_locations}")

    # vax = [v for v in vax if v.location.iloc[0] == "Pakistan"]  # DEBUG
    # Process locations
    def _process_location(df):
        monotonic_check_skip = skip_monotonic.get(df.loc[0, "location"], [])
        anomaly_check_skip = skip_anomaly.get(df.loc[0, "location"], [])
        return process_location(df, monotonic_check_skip, anomaly_check_skip)

    logger.info("Processing and exporting data...")
    vax_valid = []
    for df in vax:
        if "location" not in df:
            raise ValueError(f"Column `location` missing. df: {df.tail(5)}")
        country = df.loc[0, "location"]
        if country.lower() not in skip_complete:
            df = _process_location(df)
            vax_valid.append(df)
            # Export
            df.to_csv(paths.out_vax(country, public=True), index=False)
            logger.info(f"{country}: SUCCESS ✅")
        else:
            logger.info(f"{country}: SKIPPED 🚧")
    df = pd.concat(vax_valid).sort_values(by=["location", "date"])
    df.to_csv(paths.SCRIPTS.TMP_VAX, index=False)
    gsheet.metadata.to_csv(paths.SCRIPTS.TMP_VAX_META, index=False)
    logger.info("Exported ✅")
    print_eoe()
