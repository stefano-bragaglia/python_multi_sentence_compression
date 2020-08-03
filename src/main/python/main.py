import datetime
import itertools
import json
import re
import time
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

import spacy

Graph = Dict[str, Dict[str, Union[int, float]]]
Table = Dict[str, Tuple[int, int]]

START, END = '<START>', '<END>'


def word_graph(content: str) -> Tuple[Graph, Table]:
    def overlap(pr: str, cu: str, su: str) -> float:
        return sum(0.5 for s, e in [(pr, cu), (cu, su)]
                   if any(t.startswith(s) and any(h.startswith(e) for h in hs) for t, hs in result[0].items()))

    def occurs(el: str) -> int:
        return 0 if el not in result[1] else len(result[1][el])

    ident = itertools.count()
    result = ({}, {})
    doc = nlp(re.sub(r'\s+', ' ', content).strip())
    for idx, sent in enumerate(doc.sents):
        pred = START
        tokens = [f"{str(t).lower()}:{t.tag_}:{'*' if t.is_stop else '_'}" for t in sent if not t.is_punct]
        for pos, curr in enumerate(tokens):
            succ = tokens[pos + 1] if pos < len(tokens) - 1 else END
            candidates = [(t, overlap(pred, curr, succ), occurs(t)) for t in result[0] if t.startswith(curr)]
            if not candidates:
                candidate = f"{curr}:{next(ident)}"
            else:
                candidate, score, num = max(candidates, key=lambda x: (x[1], x[2], x[0]))
                if ':*:' in curr and score == 0:
                    candidate = f"{curr}:{next(ident)}"
            result[1].setdefault(candidate, set()).add((idx, pos))
            heads = result[0].setdefault(pred, {})
            heads[candidate] = heads.get(candidate, 0) + 1
            pred = candidate
        heads = result[0].setdefault(pred, {})
        heads[END] = heads.get(END, 0) + 1

    return result


def naive_weight(graph: Graph) -> Graph:
    result = {}
    for tail, heads in graph.items():
        total = sum(heads.values())
        result[tail] = {}
        for head, occur in heads.items():
            result[tail][head] = total / occur

    return result


def advanced_weight(graph: Graph, lookup: Table) -> Graph:
    result = {}
    for tail, heads in graph.items():
        result[tail] = {}
        for head, occur in heads.items():
            tail_refs = lookup.get(tail, set())
            head_refs = lookup.get(head, set())
            strength = 0
            for tail_ref in tail_refs:
                for head_ref in head_refs:
                    if tail_ref[0] == head_ref[0] and tail_ref[1] < head_ref[1]:
                        strength += 1 / (tail_ref[1] - head_ref[1])
            if strength:
                strength = (len(tail_refs) + len(head_refs)) / strength
            salience = 0 if strength == 0 else strength / (len(tail_refs) * len(head_refs))
            result[tail][head] = 1 - salience

    return result


def search(graph: Graph, num_results: int = 5, min_len: int = 8) -> List[Tuple[List[str], float]]:
    result, fringe = [], [([], 0)]
    while fringe:
        best = min(fringe, key=lambda x: x[1])
        fringe.remove(best)
        tail = best[0][-1] if best[0] else START
        for head, cost in graph[tail].items():
            if head in best[0]:
                continue

            if head != END:
                path = ([*best[0], head], best[1] + cost)
                if path not in fringe:
                    fringe.append(path)

            if len(best[0]) < min_len or not any(':VB' in n for n in best[0]):
                continue

            entry = (best[0], best[1] / len(best[0]))
            if entry not in result:
                result.append(entry)
            if len(result) >= num_results:
                return result

    return result


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


SENTENCES = """
The wife of a former U.S. president Bill Clinton, Hillary Clinton, visited China last Monday.
Hillary Clinton wanted to visit China last month but postponed her plans till Monday last week.
Hillary Clinton paid a visit to the People Republic of China on Monday.
Last week the Secretary State Ms. Clinton visited Chinese officials.
"""

if __name__ == '__main__':
    with Timer('Total'):
        with Timer('Load NLP'):
            nlp = spacy.load("en_core_web_sm")

        with Timer('Building'):
            g, t = word_graph(SENTENCES)

        with Timer('Weighting'):
            # graph = naive_weight(g)
            g = advanced_weight(g, t)
            # print(json.dumps(g, indent=4), end='\n\n')

        with Timer('Compressing'):
            summaries = search(g, num_results=15, min_len=8)
            if summaries:
                summaries = sorted(summaries, key=lambda x: x[1])
                for i, (summary, cost) in enumerate(summaries):
                    print(f"{i + 1:3}. (cost: {cost:.3f}) {' '.join(w.split(':')[0] for w in summary)}")
                print()

    print('Done.')
