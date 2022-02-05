import importlib

from joblib import Parallel, delayed

from cowidev.vax.manual.twitter import __all__ as twitter_countries
from cowidev.vax.manual.twitter.utils import TwitterAPI
from cowidev.vax.cmd.utils import get_logger, print_eoe


# Logger
logger = get_logger()

# Import modules
country_to_module = {c: f"cowidev.vax.manual.twitter.{c}" for c in twitter_countries}
modules_name = list(country_to_module.values())


def _propose_data_country(api, module_name: str):
    logger.info(f"{module_name}: started")
    module = importlib.import_module(module_name)
    try:
        module.main(api)
    except Exception as err:
        success = False
        logger.error(f"{module_name}: ❌ {err}", exc_info=True)
    else:
        success = True
        logger.info(f"{module_name}: SUCCESS ✅")
    return {"module_name": module_name, "success": success, "skipped": False}


def main_propose_data_twitter(
    consumer_key: str,
    consumer_secret: str,
    parallel: bool = False,
    n_jobs: int = -2,
):
    """Get data from Twitter and propose it."""
    print("-- Generating data proposals from Twitter sources... --")
    api = TwitterAPI(consumer_key, consumer_secret)
    if parallel:
        modules_execution_results = Parallel(n_jobs=n_jobs, backend="threading")(
            delayed(_propose_data_country)(
                api,
                module_name,
            )
            for module_name in modules_name
        )
    else:
        modules_execution_results = []
        for module_name in modules_name:
            modules_execution_results.append(
                _propose_data_country(
                    api,
                    module_name,
                )
            )

    modules_failed = [m["module_name"] for m in modules_execution_results if m["success"] is False]
    # Retry failed modules
    logger.info(f"\n---\n\nRETRIALS ({len(modules_failed)})")
    modules_execution_results = []
    for module_name in modules_failed:
        modules_execution_results.append(_propose_data_country(api, module_name))
    modules_failed_retrial = [m["module_name"] for m in modules_execution_results if m["success"] is False]
    if len(modules_failed_retrial) > 0:
        failed_str = "\n".join([f"* {m}" for m in modules_failed_retrial])
        print(f"\n---\n\nThe following scripts failed to run ({len(modules_failed_retrial)}):\n{failed_str}")
    print_eoe()
