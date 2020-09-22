import itertools
import re
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

from utils import NLP

Graph = Dict[str, Dict[str, Union[int, float]]]
Sentence = List[str]
Table = Dict[str, Tuple[int, int]]


def parse(content: str) -> List[Sentence]:
    result = []
    doc = NLP(re.sub(r'\s+', ' ', content).strip())
    for idx, sent in enumerate(doc.sents):
        tokens = ['<START>']
        for token in sent:
            if not token.is_punct:
                tokens.append(f"{str(token).lower()}:{token.tag_}:{'*' if token.is_stop else '_'}")
        tokens.append('<END>')
        result.append(tokens)

    return result


def encode(sentences: List[Sentence]) -> Tuple[Graph, Table]:
    def overlap(left: str, elem: str, right: str) -> float:
        return sum(0.5 for s, e in [(left, elem), (elem, right)]
                   if any(k.startswith(s) and any(v.startswith(e) for v in vv) for k, vv in graph.items()))

    def occurs(elem: str) -> int:
        return 0 if elem not in table else len(table[elem])

    graph, table = {}, {}
    ident = itertools.count()
    for idx, sentence in enumerate(sentences):
        pred = sentence[0]
        for pos, (curr, succ) in enumerate(zip(sentence[1:-1], sentence[2:-1])):
            candidates = [(k, overlap(pred, curr, succ), occurs(k)) for k in graph if k.startswith(curr)]
            if not candidates:
                candidate = f"{curr}:{next(ident)}"
            else:
                candidate, score, num = max(candidates, key=lambda x: (x[1], x[2], x[0]))
                if ':*:' in curr and score == 0:
                    candidate = f"{curr}:{next(ident)}"
            pool = graph.setdefault(pred, {})
            pool[candidate] = pool.get(candidate, 0) + 1
            table.setdefault(candidate, set()).add((idx, pos))
            pred = candidate
        pool = graph.setdefault(pred, {})
        pool[sentence[-1]] = pool.get(sentence[-1], 0) + 1

    return graph, table


def naive_weight(graph: Graph) -> Graph:
    result = {}
    for tail, heads in graph.items():
        total = sum(heads.values())
        result[tail] = {}
        for head, occur in heads.items():
            # result[tail][head] = total / occur
            result[tail][head] = 1 - occur / total

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


def traverse(graph: Graph, num_results: int = 5, min_len: int = 8) -> List[Tuple[List[str], float]]:
    result, fringe = [], [([], 0)]
    while num_results > 0 and fringe:
        best = min(fringe, key=lambda x: x[1])
        fringe.remove(best)
        tail = best[0][-1] if best[0] else '<START>'
        if tail not in graph:
            return result

        for head, cost in graph[tail].items():
            if head in best[0]:
                continue

            if head != '<END>':
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


def report(summaries: List[Tuple[Sentence, float]], num_results: int = 5) -> None:
    summaries = sorted(summaries, key=lambda x: x[1])
    for idx, (summary, cost) in enumerate(summaries, start=1):
        print(f"      {idx:3}. (cost: {cost:.3f}) {' '.join(k.split(':')[0] for k in summary)}")
        if idx > 0 and idx == num_results:
            break
