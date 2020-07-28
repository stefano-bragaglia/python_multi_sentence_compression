import datetime
import json
import os
import re
import time
from json import JSONDecodeError
from typing import Any
from typing import Dict

EXTERNAL = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/external/'))
INTERIM = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/interim/'))
PROCESSED = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/processed/'))
RAW = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/raw/'))


class Timer(object):
    """Measure time used."""

    # Ref: https://stackoverflow.com/a/57931660/

    def __init__(self, name: str = "(block)", verbose: bool = True):
        self.name = name
        self.verbose = verbose

    def __call__(self) -> float:
        return time.perf_counter() - self.start_time

    def __str__(self) -> str:
        return str(datetime.timedelta(seconds=self()))

    def __enter__(self) -> 'Timer':
        self.start_time = time.perf_counter()
        if self.verbose:
            print(f'{self.name}...')

        return self

    def __exit__(self, ty, val, tb):
        if self.verbose:
            print(f'{self.name}: completed in {self}\n')

        return False  # re-raise any exceptions
