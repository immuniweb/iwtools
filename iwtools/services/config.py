from typing import Union
from pathlib import PosixPath, Path

from services.services import Services
from services.checker import CheckerWebsec
from services.checker import CheckerSsl
# from services.checker import CheckerMobile

from lib.keys import get_config


class Config:
    @staticmethod
    def get_config(service: str, path: Union[PosixPath, None]):
        config_file = ''
        all_keys = []

        if service == Services.WEBSEC:
            config_file = Path('config/websec.yaml')
            all_keys = CheckerWebsec.ALL_KEYS
        elif service == Services.SSL:
            config_file = Path('config/ssl.yaml')
            all_keys = CheckerSsl.ALL_KEYS
        # elif service == Services.MOBILE:
        #     config_file = Path('config/mobile.yaml')
        #     all_keys = CheckerMobile.ALL_KEYS

        if path:
            config_file = path

        config_full = get_config(config_file)

        config_service = {}
        for key in all_keys:
            if key in config_full:
                config_service[key] = config_full[key]

        return config_service
