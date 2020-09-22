from unittest import TestCase

from assertpy import assert_that

from code import advanced_weight
from code import encode
from code import naive_weight
from code import parse
from code import report
from code import traverse

SENTENCES = """
The wife of a former U.S. president Bill Clinton, Hillary Clinton, visited China last Monday.
Hillary Clinton wanted to visit China last month but postponed her plans till Monday last week.
Hillary Clinton paid a visit to the People Republic of China on Monday.
Last week the Secretary State Ms. Clinton visited Chinese officials.
"""

TOKENS = [
    [
        '<START>', 'the:DT:*', 'wife:NN:_', 'of:IN:*', 'a:DT:*', 'former:JJ:*', 'u.s.:NNP:_', 'president:NN:_',
        'bill:NNP:_', 'clinton:NNP:_', 'hillary:NNP:_', 'clinton:NNP:_', 'visited:VBD:_', 'china:NNP:_', 'last:JJ:*',
        'monday:NNP:_', '<END>'
    ], [
        '<START>', 'hillary:NNP:_', 'clinton:NNP:_', 'wanted:VBD:_', 'to:TO:*', 'visit:VB:_', 'china:NNP:_',
        'last:JJ:*', 'month:NN:_', 'but:CC:*', 'postponed:VBD:_', 'her:PRP$:*', 'plans:NNS:_', 'till:IN:_',
        'monday:NNP:_', 'last:JJ:*', 'week:NN:_', '<END>'
    ], [
        '<START>', 'hillary:NNP:_', 'clinton:NNP:_', 'paid:VBD:_', 'a:DT:*', 'visit:NN:_', 'to:IN:*', 'the:DT:*',
        'people:NNP:_', 'republic:NNP:_', 'of:IN:*', 'china:NNP:_', 'on:IN:*', 'monday:NNP:_', '<END>'
    ], [
        '<START>', 'last:JJ:*', 'week:NN:_', 'the:DT:*', 'secretary:NNP:_', 'state:NNP:_', 'ms.:NNP:_', 'clinton:NNP:_',
        'visited:VBD:_', 'chinese:JJ:_', 'officials:NNS:_', '<END>'
    ]
]

GRAPH = {
    '<START>': {'the:DT:*:0': 1, 'hillary:NNP:_:9': 2, 'last:JJ:*:12': 1},
    'the:DT:*:0': {'wife:NN:_:1': 1, 'people:NNP:_:26': 1, 'secretary:NNP:_:30': 1},
    'wife:NN:_:1': {'of:IN:*:2': 1},
    'of:IN:*:2': {'a:DT:*:3': 1, 'china:NNP:_:11': 1},
    'a:DT:*:3': {'former:JJ:*:4': 1, 'visit:NN:_:24': 1},
    'former:JJ:*:4': {'u.s.:NNP:_:5': 1},
    'u.s.:NNP:_:5': {'president:NN:_:6': 1},
    'president:NN:_:6': {'bill:NNP:_:7': 1},
    'bill:NNP:_:7': {'clinton:NNP:_:8': 1},
    'clinton:NNP:_:8': {'hillary:NNP:_:9': 1, 'visited:VBD:_:10': 2, 'wanted:VBD:_:13': 1, 'paid:VBD:_:23': 1},
    'hillary:NNP:_:9': {'clinton:NNP:_:8': 3},
    'visited:VBD:_:10': {'china:NNP:_:11': 1, 'chinese:JJ:_:33': 1},
    'china:NNP:_:11': {'last:JJ:*:12': 2, 'on:IN:*:28': 1},
    'last:JJ:*:12': {'<END>': 2, 'month:NN:_:16': 1, 'week:NN:_:29': 1},
    'wanted:VBD:_:13': {'to:TO:*:14': 1},
    'to:TO:*:14': {'visit:VB:_:15': 1},
    'visit:VB:_:15': {'china:NNP:_:11': 1},
    'month:NN:_:16': {'but:CC:*:17': 1},
    'but:CC:*:17': {'postponed:VBD:_:18': 1},
    'postponed:VBD:_:18': {'her:PRP$:*:19': 1},
    'her:PRP$:*:19': {'plans:NNS:_:20': 1},
    'plans:NNS:_:20': {'till:IN:_:21': 1},
    'till:IN:_:21': {'monday:NNP:_:22': 1},
    'monday:NNP:_:22': {'last:JJ:*:12': 1},
    'paid:VBD:_:23': {'a:DT:*:3': 1},
    'visit:NN:_:24': {'to:IN:*:25': 1},
    'to:IN:*:25': {'the:DT:*:0': 1},
    'people:NNP:_:26': {'republic:NNP:_:27': 1},
    'republic:NNP:_:27': {'of:IN:*:2': 1},
    'on:IN:*:28': {'<END>': 1},
    'week:NN:_:29': {'the:DT:*:0': 1},
    'secretary:NNP:_:30': {'state:NNP:_:31': 1},
    'state:NNP:_:31': {'ms.:NNP:_:32': 1},
    'ms.:NNP:_:32': {'clinton:NNP:_:8': 1},
    'chinese:JJ:_:33': {'<END>': 1},
}

TABLE = {
    'the:DT:*:0': {(3, 2), (2, 6), (0, 0)},
    'wife:NN:_:1': {(0, 1)},
    'of:IN:*:2': {(2, 9), (0, 2)},
    'a:DT:*:3': {(2, 3), (0, 3)},
    'former:JJ:*:4': {(0, 4)},
    'u.s.:NNP:_:5': {(0, 5)},
    'president:NN:_:6': {(0, 6)},
    'bill:NNP:_:7': {(0, 7)},
    'clinton:NNP:_:8': {(2, 1), (0, 10), (1, 1), (3, 6), (0, 8)},
    'hillary:NNP:_:9': {(1, 0), (0, 9), (2, 0)},
    'visited:VBD:_:10': {(3, 7), (0, 11)},
    'china:NNP:_:11': {(0, 12), (2, 10), (1, 5)},
    'last:JJ:*:12': {(0, 13), (1, 6), (1, 14), (3, 0)},
    'wanted:VBD:_:13': {(1, 2)},
    'to:TO:*:14': {(1, 3)},
    'visit:VB:_:15': {(1, 4)},
    'month:NN:_:16': {(1, 7)},
    'but:CC:*:17': {(1, 8)},
    'postponed:VBD:_:18': {(1, 9)},
    'her:PRP$:*:19': {(1, 10)},
    'plans:NNS:_:20': {(1, 11)},
    'till:IN:_:21': {(1, 12)},
    'monday:NNP:_:22': {(1, 13)},
    'paid:VBD:_:23': {(2, 2)},
    'visit:NN:_:24': {(2, 4)},
    'to:IN:*:25': {(2, 5)},
    'people:NNP:_:26': {(2, 7)},
    'republic:NNP:_:27': {(2, 8)},
    'on:IN:*:28': {(2, 11)},
    'week:NN:_:29': {(3, 1)},
    'secretary:NNP:_:30': {(3, 3)},
    'state:NNP:_:31': {(3, 4)},
    'ms.:NNP:_:32': {(3, 5)},
    'chinese:JJ:_:33': {(3, 8)},
}

NAIVE_WEIGHT = {
    '<START>': {'the:DT:*:0': 0.75, 'hillary:NNP:_:9': 0.5, 'last:JJ:*:12': 0.75},
    'the:DT:*:0': {
        'wife:NN:_:1': 0.6666666666666667,
        'people:NNP:_:26': 0.6666666666666667,
        'secretary:NNP:_:30': 0.6666666666666667,
    },
    'wife:NN:_:1': {'of:IN:*:2': 0.0},
    'of:IN:*:2': {'a:DT:*:3': 0.5, 'china:NNP:_:11': 0.5},
    'a:DT:*:3': {'former:JJ:*:4': 0.5, 'visit:NN:_:24': 0.5},
    'former:JJ:*:4': {'u.s.:NNP:_:5': 0.0},
    'u.s.:NNP:_:5': {'president:NN:_:6': 0.0},
    'president:NN:_:6': {'bill:NNP:_:7': 0.0},
    'bill:NNP:_:7': {'clinton:NNP:_:8': 0.0},
    'clinton:NNP:_:8': {'hillary:NNP:_:9': 0.8, 'visited:VBD:_:10': 0.6, 'wanted:VBD:_:13': 0.8, 'paid:VBD:_:23': 0.8},
    'hillary:NNP:_:9': {'clinton:NNP:_:8': 0.0},
    'visited:VBD:_:10': {'china:NNP:_:11': 0.5, 'chinese:JJ:_:33': 0.5},
    'china:NNP:_:11': {'last:JJ:*:12': 0.33333333333333337, 'on:IN:*:28': 0.6666666666666667},
    'last:JJ:*:12': {'<END>': 0.5, 'month:NN:_:16': 0.75, 'week:NN:_:29': 0.75},
    'wanted:VBD:_:13': {'to:TO:*:14': 0.0},
    'to:TO:*:14': {'visit:VB:_:15': 0.0},
    'visit:VB:_:15': {'china:NNP:_:11': 0.0},
    'month:NN:_:16': {'but:CC:*:17': 0.0},
    'but:CC:*:17': {'postponed:VBD:_:18': 0.0},
    'postponed:VBD:_:18': {'her:PRP$:*:19': 0.0},
    'her:PRP$:*:19': {'plans:NNS:_:20': 0.0},
    'plans:NNS:_:20': {'till:IN:_:21': 0.0},
    'till:IN:_:21': {'monday:NNP:_:22': 0.0},
    'monday:NNP:_:22': {'last:JJ:*:12': 0.0},
    'paid:VBD:_:23': {'a:DT:*:3': 0.0},
    'visit:NN:_:24': {'to:IN:*:25': 0.0},
    'to:IN:*:25': {'the:DT:*:0': 0.0},
    'people:NNP:_:26': {'republic:NNP:_:27': 0.0},
    'republic:NNP:_:27': {'of:IN:*:2': 0.0},
    'on:IN:*:28': {'<END>': 0.0},
    'week:NN:_:29': {'the:DT:*:0': 0.0},
    'secretary:NNP:_:30': {'state:NNP:_:31': 0.0},
    'state:NNP:_:31': {'ms.:NNP:_:32': 0.0},
    'ms.:NNP:_:32': {'clinton:NNP:_:8': 0.0},
    'chinese:JJ:_:33': {'<END>': 0.0},
}

ADVANCE_WEIGHT = {
    '<START>': {'the:DT:*:0': 1, 'hillary:NNP:_:9': 1, 'last:JJ:*:12': 1},
    'the:DT:*:0': {
        'wife:NN:_:1': 2.333333333333333,
        'people:NNP:_:26': 2.333333333333333,
        'secretary:NNP:_:30': 2.333333333333333,
    },
    'wife:NN:_:1': {'of:IN:*:2': 2.5},
    'of:IN:*:2': {'a:DT:*:3': 2.0, 'china:NNP:_:11': 1.7575757575757573},
    'a:DT:*:3': {'former:JJ:*:4': 2.5, 'visit:NN:_:24': 2.5},
    'former:JJ:*:4': {'u.s.:NNP:_:5': 3.0},
    'u.s.:NNP:_:5': {'president:NN:_:6': 3.0},
    'president:NN:_:6': {'bill:NNP:_:7': 3.0},
    'bill:NNP:_:7': {'clinton:NNP:_:8': 1.9},
    'clinton:NNP:_:8': {
        'hillary:NNP:_:9': 1.5333333333333332,
        'visited:VBD:_:10': 1.3,
        'wanted:VBD:_:13': 2.2,
        'paid:VBD:_:23': 2.2,
    },
    'hillary:NNP:_:9': {'clinton:NNP:_:8': 1.1777777777777778},
    'visited:VBD:_:10': {'china:NNP:_:11': 1.8333333333333335, 'chinese:JJ:_:33': 2.5},
    'china:NNP:_:11': {'last:JJ:*:12': 1.2763157894736843, 'on:IN:*:28': 2.333333333333333},
    'last:JJ:*:12': {'<END>': 1, 'month:NN:_:16': 2.25, 'week:NN:_:29': 2.25},
    'wanted:VBD:_:13': {'to:TO:*:14': 3.0},
    'to:TO:*:14': {'visit:VB:_:15': 3.0},
    'visit:VB:_:15': {'china:NNP:_:11': 2.333333333333333},
    'month:NN:_:16': {'but:CC:*:17': 3.0},
    'but:CC:*:17': {'postponed:VBD:_:18': 3.0},
    'postponed:VBD:_:18': {'her:PRP$:*:19': 3.0},
    'her:PRP$:*:19': {'plans:NNS:_:20': 3.0},
    'plans:NNS:_:20': {'till:IN:_:21': 3.0},
    'till:IN:_:21': {'monday:NNP:_:22': 3.0},
    'monday:NNP:_:22': {'last:JJ:*:12': 2.25},
    'paid:VBD:_:23': {'a:DT:*:3': 2.5},
    'visit:NN:_:24': {'to:IN:*:25': 3.0},
    'to:IN:*:25': {'the:DT:*:0': 2.333333333333333},
    'people:NNP:_:26': {'republic:NNP:_:27': 3.0},
    'republic:NNP:_:27': {'of:IN:*:2': 2.5},
    'on:IN:*:28': {'<END>': 1},
    'week:NN:_:29': {'the:DT:*:0': 2.333333333333333},
    'secretary:NNP:_:30': {'state:NNP:_:31': 3.0},
    'state:NNP:_:31': {'ms.:NNP:_:32': 3.0},
    'ms.:NNP:_:32': {'clinton:NNP:_:8': 2.2},
    'chinese:JJ:_:33': {'<END>': 1},
}

NAIVE_SUMMARIES = [
    ([
         'hillary:NNP:_:9',
         'clinton:NNP:_:8',
         'wanted:VBD:_:13',
         'to:TO:*:14',
         'visit:VB:_:15',
         'china:NNP:_:11',
     ], 0.21666666666666667),
    ([
         'last:JJ:*:12',
         'month:NN:_:16',
         'but:CC:*:17',
         'postponed:VBD:_:18',
         'her:PRP$:*:19',
         'plans:NNS:_:20',
     ], 0.25),
    ([
         'last:JJ:*:12',
         'month:NN:_:16',
         'but:CC:*:17',
         'postponed:VBD:_:18',
         'her:PRP$:*:19',
         'plans:NNS:_:20',
         'till:IN:_:21',
     ], 0.21428571428571427),
    ([
         'hillary:NNP:_:9',
         'clinton:NNP:_:8',
         'wanted:VBD:_:13',
         'to:TO:*:14',
         'visit:VB:_:15',
         'china:NNP:_:11',
         'last:JJ:*:12',
     ], 0.23333333333333334),
    ([
         'hillary:NNP:_:9',
         'clinton:NNP:_:8',
         'paid:VBD:_:23',
         'a:DT:*:3',
         'former:JJ:*:4',
         'u.s.:NNP:_:5',
     ], 0.3)]

ADVANCE_SUMMARIES = [
    ([
         'hillary:NNP:_:9',
         'clinton:NNP:_:8',
         'visited:VBD:_:10',
         'china:NNP:_:11',
         'last:JJ:*:12',
         'month:NN:_:16',
     ], 1.4729044834307992),
    ([
         'hillary:NNP:_:9',
         'clinton:NNP:_:8',
         'visited:VBD:_:10',
         'china:NNP:_:11',
         'last:JJ:*:12',
         'week:NN:_:29',
     ], 1.4729044834307992),
    ([
         'hillary:NNP:_:9',
         'clinton:NNP:_:8',
         'visited:VBD:_:10',
         'china:NNP:_:11',
         'last:JJ:*:12',
         'week:NN:_:29',
         'the:DT:*:0',
     ], 1.5958228905597325),
    ([
         'hillary:NNP:_:9',
         'clinton:NNP:_:8',
         'visited:VBD:_:10',
         'china:NNP:_:11',
         'last:JJ:*:12',
         'month:NN:_:16',
         'but:CC:*:17',
     ], 1.6910609857978278),
    ([
         'hillary:NNP:_:9',
         'clinton:NNP:_:8',
         'paid:VBD:_:23',
         'a:DT:*:3',
         'former:JJ:*:4',
         'u.s.:NNP:_:5',
     ], 2.062962962962963),
]


# noinspection PyMethodMayBeStatic
class MainTest(TestCase):

    def test__parse(self):
        for i, (sentences, expected) in enumerate([
            ('', []),
            ('  \n  \n  \n  ', []),
            (SENTENCES, TOKENS),
        ]):
            with self.subTest(i=i, params=(sentences, expected)):
                result = parse(sentences)

                assert_that(result, 'parse').is_equal_to(expected)

    def test__encode(self):
        for i, (tokens, exp_graph, exp_table) in enumerate([
            ([], {}, {}),
            (TOKENS, GRAPH, TABLE),
        ]):
            with self.subTest(i=i, params=(tokens, exp_graph, exp_table)):
                graph, table = encode(tokens)

                assert_that(graph, 'encode').is_equal_to(exp_graph)
                assert_that(table, 'encode').is_equal_to(exp_table)

    def test__naive_weight(self):
        for i, (graph, expected) in enumerate([
            ({}, {}),
            (GRAPH, NAIVE_WEIGHT),
        ]):
            with self.subTest(i=i, params=(graph, expected)):
                result = naive_weight(graph)

                assert_that(result, 'naive_weight').is_equal_to(expected)

    def test__advanced_weight(self):
        for i, (graph, table, expected) in enumerate([
            ({}, {}, {}),
            (GRAPH, TABLE, ADVANCE_WEIGHT),
        ]):
            with self.subTest(i=i, params=(graph, table, expected)):
                result = advanced_weight(graph, table)

                assert_that(result, 'advanced_weight').is_equal_to(expected)

    def test__traverse(self):
        for i, (weight, results, length, expected) in enumerate([
            ({}, 0, 6, []),
            (NAIVE_WEIGHT, 0, 6, []),
            (ADVANCE_WEIGHT, 0, 6, []),
            ({}, 5, 20, []),
            (NAIVE_WEIGHT, 5, 50, []),
            (ADVANCE_WEIGHT, 5, 50, []),
            ({}, 5, 6, []),
            (NAIVE_WEIGHT, 5, 6, NAIVE_SUMMARIES),
            (ADVANCE_WEIGHT, 5, 6, ADVANCE_SUMMARIES),
        ]):
            with self.subTest(i=i, params=(weight, results, length, expected)):
                result = traverse(weight, results, length)

                assert_that(result, 'traverse').is_equal_to(expected)

    # noinspection PyBroadException
    def test__report(self):
        for i, summaries in enumerate([
            [],
            NAIVE_SUMMARIES,
            ADVANCE_SUMMARIES,
        ]):
            with self.subTest(i=i, params=(summaries)):
                try:
                    report(summaries)
                except Exception:
                    assert_that(False, 'report').is_true()
                else:
                    assert_that(True, 'report').is_true()
