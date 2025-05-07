import pytest
from agenda_based_mcfg_wchoi18.grammar import MCFGRuleElementInstance, MCFGRule, MCFGGrammar # type: ignore
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


class TestAgendaBasedMCFGParser:

    @pytest.fixture
    def test_grammar(self):
        test_rules = """
            S(uv) -> NP(u) VP(v)
            S(uv) -> NPwh(u) VP(v)
            S(vuw) -> Aux(u) Swhmain(v, w)
            S(uwv) -> NPdisloc(u, v) VP(w)
            S(uwv) -> NPwhdisloc(u, v) VP(w)
            Sbar(uv) -> C(u) S(v)
            Sbarwh(v, uw) -> C(u) Swhemb(v, w)
            Sbarwh(u, v) -> NPwh(u) VP(v)
            Swhmain(v, uw) -> NP(u) VPwhmain(v, w)
            Swhmain(w, uxv) -> NPdisloc(u, v) VPwhmain(w, x)
            Swhemb(v, uw) -> NP(u) VPwhemb(v, w)
            Swhemb(w, uxv) -> NPdisloc(u, v) VPwhemb(w, x)
            Src(v, uw) -> NP(u) VPrc(v, w)
            Src(w, uxv) -> NPdisloc(u, v) VPrc(w, x)
            Src(u, v) -> N(u) VP(v)
            Swhrc(u, v) -> Nwh(u) VP(v)
            Swhrc(v, uw) -> NP(u) VPwhrc(v, w)
            Sbarwhrc(v, uw) -> C(u) Swhrc(v, w)
            VP(uv) -> Vpres(u) NP(v)
            VP(uv) -> Vpres(u) Sbar(v)
            VPwhmain(u, v) -> NPwh(u) Vroot(v)
            VPwhmain(u, wv) -> NPwhdisloc(u, v) Vroot(w)
            VPwhmain(v, uw) -> Vroot(u) Sbarwh(v, w)
            VPwhemb(u, v) -> NPwh(u) Vpres(v)
            VPwhemb(u, wv) -> NPwhdisloc(u, v) Vpres(w)
            VPwhemb(v, uw) -> Vpres(u) Sbarwh(v, w)
            VPrc(u, v) -> N(u) Vpres(v)
            VPrc(v, uw) -> Vpres(u) Nrc(v, w)
            VPwhrc(u, v) -> Nwh(u) Vpres(v)
            VPwhrc(v, uw) -> Vpres(u) Sbarwhrc(v, w)
            NP(uv) -> D(u) N(v)
            NP(uvw) -> D(u) Nrc(v, w)
            NPdisloc(uv, w) -> D(u) Nrc(v, w)
            NPwh(uv) -> Dwh(u) N(v)
            NPwh(uvw) -> Dwh(u) Nrc(v, w)
            NPwhdisloc(uv, w) -> Dwh(u) Nrc(v, w)
            Nrc(v, uw) -> C(u) Src(v, w)
            Nrc(u, vw) -> N(u) Swhrc(v, w)
            Nrc(u, vwx) -> Nrc(u, v) Swhrc(w, x)
            Dwh(which)
            NPwh(who)
            D(the)
            D(a)
            N(greyhound)
            N(human)
            Vpres(believes)
            Vroot(believe)
            Aux(does)
            C(that)
        """
        rules = [MCFGRule.from_string(line.strip()) for line in test_rules.splitlines() if '(' in line]

        return MCFGGrammar(
            alphabet={"which", "who", "the", "a", "greyhound", "human", "believes", "believe", "does", "that"},
            variables={"S", "Sbar", "Sbarwh", "Swhmain", "Swhemb", "Src", "Swhrc", "VP", "VPwhmain", "VPwhemb",
                    "VPrc", "VPwhrc", "NP", "NPdisloc", "NPwh", "Nrc"},
            rules=set(rules),
            start_variable='S'
        )

    def test_parser(self, test_grammar):
        parser = AgendaBasedMCFGParser(test_grammar)
        tokens = ["who", "does", "the", "greyhound", "believe"]
        trees = parser.parse(tokens)
        assert len(trees) > 0
        for tree in trees:
            assert tree.data == "S"
