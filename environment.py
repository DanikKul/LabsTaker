from typing import Dict
from dotenv import load_dotenv
from os import getenv


class Environment:
    def __init__(self, envs: Dict[str, str]):
        if not load_dotenv():
            raise RuntimeError("missing .env in cwd")

        self.__env: Dict[str, str] = {}

        for envname, envkey in envs.items():
            value: (str | None) = getenv(envkey)

            if value is not None:
                self.__env.update({envname: value})

    def __getitem__(self, item):
        return self.__env[item]
