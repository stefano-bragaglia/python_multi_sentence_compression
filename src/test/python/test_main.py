from unittest import TestCase

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


# noinspection PyMethodMayBeStatic
class MainTest(TestCase):

    def test__parse(self):
        c = parse(SENTENCES)

        assert c

    def test__encode(self):
        c = parse(SENTENCES)
        g, t = encode(c)

        assert g
        assert t

    def test__naive_weight(self):
        c = parse(SENTENCES)
        g, t = encode(c)
        w_n = naive_weight(g)

        assert w_n

    def test__advanced_weight(self):
        c = parse(SENTENCES)
        g, t = encode(c)
        w_a = advanced_weight(g, t)

        assert w_a

    def test__search(self):
        c = parse(SENTENCES)
        g, t = encode(c)
        w_n = naive_weight(g)
        w_a = advanced_weight(g, t)
        s_n = traverse(w_n, 5, 6)
        s_a = traverse(w_a, 5, 6)

        assert s_n
        assert s_a

    def test__report(self):
        c = parse(SENTENCES)
        g, t = encode(c)
        w_n = naive_weight(g)
        w_a = advanced_weight(g, t)
        s_n = traverse(w_n, 5, 6)
        s_a = traverse(w_a, 5, 6)
        report(s_n, 5)
        report(s_a, 5)

        assert True
