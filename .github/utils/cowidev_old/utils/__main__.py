from cowidev.vax.cmd._config import get_config
from cowidev.vax.cmd import main_get_data, main_process_data, main_generate_dataset
from cowidev.vax.cmd.export import main_export
from cowidev.vax.cmd.twitter import main_propose_data_twitter
from cowidev.vax.cmd.check_with_r import test_check_with_r


def main():
    config = get_config()
    creds = config.CredentialsConfig()

    if config.display:
        print(config)

    print(config.mode)

    if "get" in config.mode:
        cfg = config.GetDataConfig()
        main_get_data(
            parallel=cfg.parallel,
            n_jobs=cfg.njobs,
            modules_name=cfg.countries,
            skip_countries=cfg.skip_countries,
            gsheets_api=config.gsheets_api,
        )
    if "process" in config.mode:
        cfg = config.ProcessDataConfig()
        main_process_data(
            gsheets_api=config.gsheets_api,
            google_spreadsheet_vax_id=creds.google_spreadsheet_vax_id,
            skip_complete=cfg.skip_complete,
            skip_monotonic=cfg.skip_monotonic_check,
            skip_anomaly=cfg.skip_anomaly_check,
        )
    if "generate" in config.mode:
        if config.check_r:
            test_check_with_r()
        else:
            main_generate_dataset()
    if "export" in config.mode:
        main_export(url=creds.owid_cloud_table_post)
    if "propose" in config.mode:
        cfg = config.ProposeDataConfig()
        main_propose_data_twitter(
            consumer_key=creds.twitter_consumer_key,
            consumer_secret=creds.twitter_consumer_secret,
            parallel=cfg.parallel,
            n_jobs=cfg.njobs,
        )


if __name__ == "__main__":
    main()
