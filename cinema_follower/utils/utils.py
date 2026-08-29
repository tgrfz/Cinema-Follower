import json
import logging
from pathlib import Path

SECRETS_PATH = Path(__file__).resolve().parent.parent.joinpath('data', 'secrets.json')


def get_secrets(key: str) -> str | dict:  # TODO switch to envvar
    logging.method('utils.utils.get_secrets')
    with open(SECRETS_PATH) as f:
        return json.load(f)[key]
