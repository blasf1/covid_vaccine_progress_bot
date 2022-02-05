import os
import json
from datetime import date
from pyaml_env import parse_config
from itertools import chain

from cowidev.vax.utils.gsheets import GSheetApi
from cowidev.vax.cmd.get_data import (
    modules_name,
    modules_name_batch,
    modules_name_incremental,
    country_to_module,
)
from cowidev.vax.cmd._parser import _parse_args, CHOICES
from cowidev.vax.cmd.utils import normalize_country_name


def get_config():
    args = _parse_args()
    return ConfigParams.from_args(args)


class ConfigParamsStep(object):
    def __init__(self, adict):
        self._dict = adict
        self.__dict__.update(adict)

    def __str__(self):
        def _is_secret(name):
            secret_keys = ["id", "token", "credentials", "credential", "secret"]
            return any(x in name for x in secret_keys)

        return f"\n".join(
            [f"* {k}: {v}" for k, v in self._dict.items() if not _is_secret(k)]
        )


class ConfigParams(object):
    def __init__(
        self,
        config_file,
        parallel,
        njobs,
        countries,
        mode,
        display,
        credentials_file,
        check_r=False,
    ):
        self._parallel = parallel
        self._njobs = njobs
        self._countries = countries
        self.mode = mode
        self.display = display
        self.check_r = check_r
        # Config file
        self.config_file = config_file
        self._config = self._load_yaml()
        self.project_dir = self._get_project_dir_from_config()
        # Credentials file
        self.credentials_file = self._get_credentials_file_from_config(credentials_file)
        self._credentials = self._load_json_credentials()

    @classmethod
    def from_args(cls, args):
        mode = args.mode
        if mode == "all":
            mode = CHOICES
        return cls(
            config_file=args.config,
            parallel=args.parallel,
            njobs=args.njobs,
            countries=args.countries,
            mode=mode,
            display=args.show_config,
            credentials_file=args.credentials,
            check_r=args.checkr,
        )

    @property
    def config_file_exists(self):
        return os.path.isfile(self.config_file)

    @property
    def credentials_file_exists(self):
        return os.path.isfile(self.credentials_file)

    @property
    def google_credential_file(self):
        field = "google_credentials"
        if field in self._credentials:
            return self._credentials[field]
        else:
            raise ValueError(
                f"Field 'google_credentials' not found in credentials file. Please check."
            )

    @property
    def gsheets_api(self):
        return GSheetApi(self.google_credential_file)

    def _get_project_dir_from_config(self):
        try:
            return self._config["global"]["project_dir"]
        except KeyError:
            print(self._config)
            raise KeyError("Missing global.project_dir variable in config.yaml")

    def _get_credentials_file_from_config(self, credentials):
        try:
            return self._config["global"]["credentials"]
        except KeyError:
            return credentials

    def _load_yaml(self):
        if self.config_file_exists:
            return parse_config(self.config_file, raise_if_na=False)
        return {}

    def _load_json_credentials(self):
        if self.credentials_file_exists:
            with open(self.credentials_file) as f:
                return json.load(f)
        else:
            raise FileNotFoundError(
                f"Credentials file not found. Check path {self.credentials_file}. We recommend"
                "setting this in `config.yaml`."
            )

    def GetDataConfig(self):
        """Use `_token`/`id`/`secret` for variables that are secret"""
        return ConfigParamsStep(
            {
                "parallel": self._return_value_pipeline(
                    "get-data", "parallel", self._parallel
                ),
                "njobs": self._return_value_pipeline("get-data", "njobs", self._njobs),
                "countries": _countries_to_modules(
                    self._return_value_pipeline(
                        "get-data", "countries", self._countries
                    )
                ),
                "skip_countries": list(
                    map(
                        normalize_country_name,
                        self._return_value_pipeline("get-data", "skip_countries", []),
                    )
                ),
            }
        )

    def ProposeDataConfig(self):
        """Use `_token`/`id`/`secret` for variables that are secret"""
        return ConfigParamsStep(
            {
                "parallel": self._return_value_pipeline(
                    "get-data", "parallel", self._parallel
                ),
                "njobs": self._return_value_pipeline("get-data", "njobs", self._njobs),
                "countries": _countries_to_modules(
                    self._return_value_pipeline(
                        "get-data", "countries", self._countries
                    )
                ),
                "skip_countries": list(
                    map(
                        normalize_country_name,
                        self._return_value_pipeline("get-data", "skip_countries", []),
                    )
                ),
            }
        )

    def ProcessDataConfig(self):
        """Use `_token`/`id`/`secret` for variables that are secret"""
        return ConfigParamsStep(
            {
                "skip_complete": self._return_value_pipeline(
                    "process-data", "skip_complete", []
                ),
                "skip_monotonic_check": self._get_skip_check("skip_monotonic_check"),
                "skip_anomaly_check": self._get_skip_check("skip_anomaly_check"),
            }
        )

    def CredentialsConfig(self):
        """Use `_token`/`id`/`secret` for variables that are secret"""
        return ConfigParamsStep(
            {
                "greece_api_token": self._return_value_credentials("greece_api_token"),
                "owid_cloud_table_post": self._return_value_credentials(
                    "owid_cloud_table_post"
                ),
                "google_credentials": self._return_value_credentials(
                    "google_credentials"
                ),
                "google_spreadsheet_vax_id": self._return_value_credentials(
                    "google_spreadsheet_vax_id"
                ),
                "twitter_consumer_key": self._return_value_credentials(
                    "twitter_consumer_key"
                ),
                "twitter_consumer_secret": self._return_value_credentials(
                    "twitter_consumer_secret"
                ),
            }
        )

    def _return_value_credentials(self, feature_name):
        if feature_name in self._credentials:
            v = self._credentials[feature_name]
            if v:
                return v
        raise AttributeError(
            f"Missing field {feature_name} or value was None in credentials"
        )

    def _get_skip_check(self, metric):
        def _valid_value(x):
            if not isinstance(x, list):
                return False
            keys = list(chain.from_iterable(xx.keys() for xx in x))
            if set(keys).difference({"date", "metrics"}):
                return False
            if not all(isinstance(xx["metrics"], (list, str)) for xx in x):
                return False
            if not all(isinstance(xx["date"], date) for xx in x):
                return False
            return True

        x = self._return_value_pipeline("process-data", metric, {})
        for _, v in x.items():
            if v is None:
                raise ValueError(
                    f"Field {metric} must be a dictionary with list values. Each element in list values "
                    "is expected to be a dictionary of shape {'date': YYYY-MM-DD, 'metrics': metrics}. `metrics` "
                    f"can be either a single string or a list of strings. Given was {x}"
                )
            elif not _valid_value(v):
                raise ValueError(
                    f"Field {metric} must be a dictionary with list values. Each element in list values "
                    "is expected to be a dictionary of shape {'date': YYYY-MM-DD, 'metrics': metrics}. `metrics` "
                    f"can be either a single string or a list of strings. Given was {x}"
                )
        return x

    def _return_value_pipeline(self, step, feature_name, feature_from_args):
        try:
            v = self._config["pipeline"][step][feature_name]
            if v is not None:
                return v
            else:
                return feature_from_args
        except KeyError:
            return feature_from_args

    def __str__(self):
        if self.config_file_exists:
            s = f"CONFIGURATION PARAMS:\nfile: {self.config_file}\n\n"
            s += "*************************\n"
        else:
            s = f"CONFIGURATION PARAMS:\nNo config file\n\n"
            s += "*************************\n"
        if "get" in self.mode:
            s += f"Get Data: \n{self.GetDataConfig().__str__()}"
        if "process" in self.mode:
            s += f"Process Data: \n{self.ProcessDataConfig().__str__()}"
        s += "\n*************************\n\n"
        # s += f"Secrets: \n{self.CredentialsConfig().__str__()}"
        return s


def _countries_to_modules(countries):
    if len(countries) == 1:
        if countries[0] == "all":
            return modules_name
        elif countries[0] == "incremental":
            return modules_name_incremental
        elif countries[0] == "batch":
            return modules_name_batch
    if len(countries) >= 1:
        # Verify validity of countries
        countries_wrong = [c for c in countries if c not in country_to_module]
        countries_valid = sorted(list(country_to_module.keys()))
        if countries_wrong:
            print(
                f"Invalid countries: {countries_wrong}. Valid countries are: {countries_valid}"
            )
            raise ValueError("Invalid country")
        # Get module equivalent names
        modules = [country_to_module[country] for country in countries]
        return modules
