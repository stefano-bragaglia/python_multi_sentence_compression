from unittest import TestCase

from main import advanced_weight
from main import naive_weight
from main import search
from main import word_graph

SENTENCES = """
The wife of a former U.S. president Bill Clinton, Hillary Clinton, visited China last Monday.
Hillary Clinton wanted to visit China last month but postponed her plans till Monday last week.
Hillary Clinton paid a visit to the People Republic of China on Monday.
Last week the Secretary State Ms. Clinton visited Chinese officials.
"""


# noinspection PyMethodMayBeStatic
class MainTest(TestCase):

    def test__word_graph(self):
        word_graph(SENTENCES)

        assert True

    def test__naive_weight(self):
        g, t = word_graph(SENTENCES)
        naive_weight(g)

        assert True

    def test__advanced_weight(self):
        g, t = word_graph(SENTENCES)
        advanced_weight(g, t)

        assert True

    def test__search(self):
        g, t = word_graph(SENTENCES)
        g = naive_weight(g)
        search(g, 5, 6)
