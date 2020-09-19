import datetime
import time

import spacy


class Timer(object):
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


with Timer('NLP Loading'):
    NLP = spacy.load("en_core_web_sm")
