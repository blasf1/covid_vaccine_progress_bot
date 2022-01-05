import argparse
import os
from difflib import SequenceMatcher

from cowidev.vax.cmd.utils import normalize_country_name, get_logger


CHOICES = ["get", "process", "generate", "export", "propose"]
logger = get_logger()


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def choice_check(x):
    x = x.lower()
    if x not in CHOICES:
        similarities = []
        for choice in CHOICES:
            if choice in x:
                logger.error(f"Mode `{x}` is unknown. Maybe you meant `{choice}`")
            similarities.append(similar(x, choice))
        i = similarities.index(max(similarities))
        if similarities[i] >= 0.6:
            logger.error(f"Mode `{x}` is unknown. Did you mean `{CHOICES[i]}` instead?")
    return x


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Execute COVID-19 vaccination data collection pipeline.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "mode",
        choices=CHOICES + ["all"],
        default="all",
        nargs="*",
        type=lambda x: choice_check(x),
        help=(
            "Choose a step: i) `get` will run automated scripts, 2) `process` will get csvs generated in 1"
            " and collect all data from spreadsheet, 3) `generate` generate the output files, 4) `export`"
            " to generate all final files, 5) `all` will  run all steps sequentially + step 6, 6) `propose` Get data"
            " from Social Networks (Twitter, Facebook) and propose data."
        ),
    )
    parser.add_argument(
        "-c",
        "--countries",
        default="all",
        type=lambda x: [normalize_country_name(ss) for ss in x.split(",")],
        help=(
            "Run for a specific country. For a list of countries use commas to separate them (only in mode get-data)"
            "E.g.: peru, norway. \nSpecial keywords: 'all' to run all countries, 'incremental' to run incremental"
            "updates, 'batch' to run batch updates, 'who' for WHO-sourced countries, 'spc' for SPC-sourced countries. Defaults to all countries."
        ),
    )
    parser.add_argument(
        "-p",
        "--parallel",
        action="store_true",
        help="Execution done in parallel (only in mode get-data).",
    )
    parser.add_argument(
        "-j",
        "--njobs",
        default=-2,
        help=(
            "Number of jobs for parallel processing. Check Parallel class in joblib library for more info  (only in "
            "mode get-data)."
        ),
    )
    parser.add_argument(
        "-s",
        "--show-config",
        action="store_true",
        help="Display configuration parameters at the beginning of the execution.",
    )
    parser.add_argument(
        "--config",
        default=(
            os.environ.get(
                "OWID_COVID_VAX_CONFIG_FILE",
                os.path.join(
                    os.path.expanduser("~"), ".config", "cowid", "config.yaml"
                ),
            )
        ),
        help=(
            "Path to config file (YAML). Will look for file in path given by environment variable "
            "`$OWID_COVID_VAX_CONFIG_FILE`. If not set, will default to ~/.config/cowid/config.yaml"
        ),
    )
    parser.add_argument(
        "--credentials",
        default="vax_dataset_config.json",
        help=(
            "Path to credentials file (JSON). If a config file is being used, the value ther will be prioritized."
        ),
    )
    parser.add_argument(
        "--checkr",
        action="store_true",
        help=(
            "Compare results from generate-dataset with results obtained with former generate_dataset.R script."
            "It requires that the R script is previously run (without removing temporary files vax & metadata)!"
        ),
    )
    args = parser.parse_args()
    return args
