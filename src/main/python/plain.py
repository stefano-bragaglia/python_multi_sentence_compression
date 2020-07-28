import itertools
import json
import os
import re
from math import inf
from typing import Callable
from typing import Dict
from typing import List

import spacy

from utils import EXTERNAL
from utils import Timer


def word_graph(content: str) -> Dict[str, Dict[str, int]]:
    result = {}
    num = itertools.count()
    doc = nlp(content)
    for sent in doc.sents:
        current = '<start>'
        for word in sent:
            if word.is_punct:
                continue

            ident = f"{str(word).lower()}:{next(num) if word.is_stop else word.tag_}"
            heads = result.setdefault(current, {})
            heads[ident] = heads.get(ident, 0) + 1
            current = ident
        heads = result.setdefault(current, {})
        heads['<end>'] = heads.get('<end>', 0) + 1

    return result


def naive_weight(graph: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, float]]:
    result = {}
    for tail, heads in graph.items():
        total = sum(heads.values())
        result[tail] = {}
        for head, occur in heads.items():
            result[tail][head] = 1 - (occur / total)

    return result


def heuristic(current: str, origin: Dict[str, str]) -> float:
    result, path = 0, traverse(current, origin)
    if len(path) < 8:
        result += 8
    if not any(':VB' in step for step in path):
        result += 8

    return result


def traverse(current: str, origin: Dict[str, str]) -> List[str]:
    result = []
    while current in origin:
        current = origin[current]
        if ':' in current:
            result = [current, *result]

    return result


def search(graph: Dict[str, Dict[str, float]], heuristic: Callable) -> List[str]:
    fringe = {'<start>'}
    origin = {}
    score = {'<start>': 0}
    esteem = {'<start>': heuristic('<start>', origin)}

    while fringe:
        current = min(fringe, key=lambda x: esteem.get(x, inf))
        if current == '<end>':
            return traverse(current, origin)

        fringe.remove(current)
        for neighbour, cost in graph.get(current, {}).items():
            tentative = score.get(current, inf) + cost
            if tentative < score.get(neighbour, inf):
                origin[neighbour] = current
                score[neighbour] = tentative
                esteem[neighbour] = tentative + heuristic(neighbour, origin)
                fringe.add(neighbour)

    raise ValueError()


if __name__ == '__main__':
    with Timer('Load NLP'):
        nlp = spacy.load("en_core_web_sm")

    with Timer('Load content'):
        with open(os.path.join(EXTERNAL, 'sentences.txt'), 'r') as file:
            content = re.sub(r'\s+', ' ', file.read()).strip()

    with Timer('Building'):
        graph = word_graph(content)

    with Timer('Weighting'):
        weighted = naive_weight(graph)

    with Timer('Compressing'):
        summary = search(weighted, heuristic)

    print(json.dumps(weighted, indent=4))

    print(' '.join(summary))

    print('Done.')
