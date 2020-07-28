import json
from collections import Counter
from typing import Dict
from typing import List

import spacy
from neo4j import GraphDatabase
from neo4j import Transaction
from spacy.symbols import ADJ
from spacy.symbols import ADP
from spacy.symbols import NOUN
from spacy.symbols import PROPN
from wikipediaapi import Wikipedia

from utils import Timer


def hello_world(out):
    out.write("Hello world of Python\n")


def get_chunks(content: str, resolve: bool = False, filter: bool = False) -> Dict[str, int]:
    if not content:
        return {}

    result = {}
    for chunk in nlp(content).noun_chunks:
        name = ' '.join(w.lemma_.lower() for w in chunk if w.pos in [ADJ, ADP, NOUN, PROPN])
        if name and all(c.isalnum() or c == ' ' for c in name):
            result[name] = result.get(name, 0) + 1
    if resolve:
        terms, acronyms = {}, set()
        for name, occur in result.items():
            acronym = ''.join(w[0] for w in name.split())
            terms[name] = occur
            if len(acronym) > 1 and acronym in result:
                terms[name] += result.get(acronym, 0)
                acronyms.add(acronym)
        for acronym in acronyms:
            terms.pop(acronym)
        result = terms

    if filter:
        threshold = round(5 * max(result.values()) / 100)
        result = {k: v for k, v in sorted(result.items(), key=lambda x: (-x[1], x[0])) if v >= threshold}

    return result


def get_count(tx: Transaction, term: str, exact: bool = False) -> Dict[str, int]:
    result = tx.run(f"MATCH (n) "
                    f"WHERE toLower(n.desc) {'=' if exact else 'CONTAINS'} {json.dumps(term)} "
                    f"WITH labels(n) AS labs "
                    f"UNWIND labs AS lab "
                    f"RETURN DISTINCT lab, count(lab) "
                    f"ORDER BY count(lab) DESC;")
    if not result:
        return {}

    return {r['lab']: r['count(lab)'] for r in result}


def get_desc(tx: Transaction, label: str, term: str) -> List[str]:
    result = tx.run(f"MATCH (n:{label}) "
                    f"WHERE toLower(n.desc) CONTAINS {json.dumps(term)} "
                    f"RETURN n.desc "
                    f"ORDER BY n.desc "
                    f"LIMIT 10;")
    if not result:
        return []

    return [r['n.desc'] for r in result]


# TITLE = 'Acute Severe Asthma'
TITLE = 'Chronic kidney disease'

if __name__ == '__main__':
    driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "password"))
    nlp = spacy.load("en_core_web_sm")
    with Timer('Fetching'):
        print()
        wiki = Wikipedia('en')
        page = wiki.page(TITLE)
        print(page.title)
        print(page.fullurl)
        print('-' * max(len(page.title), len(page.fullurl)))
        print()
        if page.exists():
            chunks = Counter(get_chunks(page.text, True, True))
            with driver.session() as session:
                for term, occur in chunks.items():
                    print(f"{term.upper()} ({occur:,} occur/s)")
                    exact = session.read_transaction(get_count, term, True)
                    approx = session.read_transaction(get_count, term, False)
                    if not exact and not approx:
                        print("  No matches")
                    else:
                        print(f"  ## | {'Exact matches:':32} | {'Partial matches':32} | Descriptions ")
                        ex = list(exact.keys()) + ['' for _ in range(max(0, len(approx) - len(exact)))]
                        ap = list(approx.keys()) + ['' for _ in range(max(0, len(exact) - len(approx)))]
                        for i, (ke, ka) in enumerate(zip(ex, ap)):
                            if ka:
                                desc = session.read_transaction(get_desc, ka, term)
                                if approx[ka] > 10:
                                    desc.append('...')
                                if ke:
                                    print(f"  {i + 1:>2}"
                                          f" | ({exact[ke]:>4}) {ke:25}"
                                          f" | ({approx[ka]:>4}) {ka:25}"
                                          f" | {', '.join(desc)}")
                                else:
                                    print(f"  {i + 1:>2}"
                                          f" | {'':>6} {'':25}"
                                          f" | ({approx[ka]:>4}) {ka:25}"
                                          f" | {', '.join(desc)}")
                            else:
                                print(f"  {i + 1:>2}"
                                      f" | ({exact[ke]:>4}) {ke:25}"
                                      f" | {'':>6} {'':25}"
                                      f" | {''}")
                    print()
        print()

    print()
    print('Done.')
