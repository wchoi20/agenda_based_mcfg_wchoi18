import pytest
from agenda_based_mcfg_wchoi18.grammar import MCFGRuleElementInstance # type: ignore
from agenda_based_mcfg_wchoi18.parser import MCFGChartEntry, MCFGChart, AgendaBasedMCFGParser # type: ignore

class TestMCFGChartEntry:

    @pytest.fixture
    def entry(self):
        instance = MCFGRuleElementInstance("VP", (1, 3))
        return MCFGChartEntry(instance)

    def test_symbol_property(self, entry):
        assert entry.symbol == "VP"

    def test_spans_property(self, entry):
        assert entry.spans == ((1, 3),)

    def test_equality(self):
        i1 = MCFGRuleElementInstance("X", (0, 2))
        i2 = MCFGRuleElementInstance("X", (0, 2))
        i3 = MCFGRuleElementInstance("Y", (0, 2))
        e1 = MCFGChartEntry(i1)
        e2 = MCFGChartEntry(i2)
        e3 = MCFGChartEntry(i3)
        assert e1 == e2
        assert e1 != e3

    def test_hash(self):
        i = MCFGRuleElementInstance("A", (0, 1))
        e = MCFGChartEntry(i)
        assert isinstance(hash(e), int)

    def test_to_tree(self):
        i = MCFGRuleElementInstance("A", (0, 1))
        leaf = MCFGChartEntry(i)
        parent = MCFGChartEntry(i, backpointers=[leaf])
        tree = parent.to_tree()
        assert tree.data == "A"
        assert all(isinstance(child, type(tree)) for child in tree.children)


class TestMCFGChart:

    @pytest.fixture
    def chart(self):
        return MCFGChart()

    @pytest.fixture
    def entry1(self):
        inst = MCFGRuleElementInstance("NP", (0, 1))
        return MCFGChartEntry(inst)

    @pytest.fixture
    def entry2(self):
        inst = MCFGRuleElementInstance("VP", (1, 3))
        return MCFGChartEntry(inst)

    def test_add_and_get_by_symbol(self, chart, entry1, entry2):
        chart.add(entry1)
        chart.add(entry2)
        assert entry1 in chart.get_by_symbol("NP")
        assert entry2 in chart.get_by_symbol("VP")
        assert chart.get_by_symbol("S") == []

    def test_duplicate_add_does_not_duplicate(self, chart, entry1):
        chart.add(entry1)
        chart.add(entry1)
        assert len(chart.get_by_symbol("NP")) == 1

    def test_parses_empty(self, chart):
        assert chart.parses == set()

    def test_parses_returns_tree(self, chart):
        inst = MCFGRuleElementInstance("S", (0, 3))
        leaf = MCFGChartEntry(inst)
        chart.add(leaf)
        trees = chart.parses
        assert len(trees) == 1
        assert all(t.data == "S" for t in trees)
