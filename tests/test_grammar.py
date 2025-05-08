import pytest
from agenda_based_mcfg_wchoi18.grammar import MCFGGrammar, MCFGRule, MCFGRuleElement, MCFGRuleElementInstance # type: ignore

class TestMCFGRuleElement:

    @pytest.fixture
    def element(self):
        return MCFGRuleElement("NP", (0,), (1,))

    def test_variable(self, element):
        assert element.variable == "NP"

    def test_string_variables(self, element):
        assert element.string_variables == ((0,), (1,))

    def test_unique_string_variables(self, element):
        assert element.unique_string_variables == {0, 1}

    def test_str(self, element):
        assert str(element) == "NP(0, 1)"

    def test_eq(self):
        e1 = MCFGRuleElement("NP", (0,), (1,))
        e2 = MCFGRuleElement("NP", (0,), (1,))
        e3 = MCFGRuleElement("NP", (1,), (0,))
        assert e1 == e2
        assert e1 != e3

    def test_to_tuple(self, element):
        assert element.to_tuple() == ("NP", ((0,), (1,)))

    def test_hash(self, element):
        assert isinstance(hash(element), int)

    def test_property_variable(self, element):
        assert element.variable == "NP"

    def test_property_string_variables(self, element):
        assert element.string_variables == ((0,), (1,))

    def test_property_unique_string_variables(self):
        e = MCFGRuleElement("NP", (1,), (3,), (1,))
        assert e.unique_string_variables == {1, 3}

class TestMCFGRuleElementInstance:

    @pytest.fixture
    def instance(self):
        return MCFGRuleElementInstance("VP", (2, 4), (5, 6))

    def test_property_variable(self, instance):
        assert instance.variable == "VP"

    def test_property_string_spans(self, instance):
        assert instance.string_spans == ((2, 4), (5, 6))

    def test_str(self, instance):
        s = str(instance)
        assert s.startswith("VP([") and ", [" in s and s.endswith("])")

    def test_repr(self, instance):
        assert repr(instance) == str(instance)

    def test_eq_and_hash(self):
        a = MCFGRuleElementInstance("A", (1, 2))
        b = MCFGRuleElementInstance("A", (1, 2))
        c = MCFGRuleElementInstance("A", (2, 3))
        assert a == b
        assert a != c
        assert hash(a) == hash(b)

    def test_to_tuple(self, instance):
        assert instance.to_tuple() == ("VP", ((2, 4), (5, 6)))

class TestMCFGRule:

    @pytest.fixture
    def simple_rule(self):
        lhs = MCFGRuleElement("S", (0,), (1,))
        rhs1 = MCFGRuleElement("NP", (0,))
        rhs2 = MCFGRuleElement("VP", (1,))
        return MCFGRule(lhs, rhs1, rhs2)

    def test_left_side(self, simple_rule):
        assert simple_rule.left_side.variable == "S"

    def test_right_side(self, simple_rule):
        assert [e.variable for e in simple_rule.right_side] == ["NP", "VP"]

    def test_is_epsilon(self):
        lhs = MCFGRuleElement("NP", (0,))
        rule = MCFGRule(lhs)
        assert rule.is_epsilon

    def test_unique_variables(self, simple_rule):
        assert simple_rule.unique_variables == {"S", "NP", "VP"}

    def test_str_and_repr(self, simple_rule):
        s = str(simple_rule)
        assert "S(" in s and "->" in s
        assert repr(simple_rule).startswith("<Rule:")

    def test_eq_and_hash(self):
        lhs = MCFGRuleElement("S", (0,), (1,))
        rhs1 = MCFGRuleElement("NP", (0,))
        rhs2 = MCFGRuleElement("VP", (1,))
        rule1 = MCFGRule(lhs, rhs1, rhs2)
        rule2 = MCFGRule(lhs, rhs1, rhs2)
        assert rule1 == rule2
        assert hash(rule1) == hash(rule2)

    def test_to_tuple(self, simple_rule):
        tpl = simple_rule.to_tuple()
        assert isinstance(tpl, tuple)
        assert tpl[0].variable == "S"

    def test_instantiate_left_side(self):
        rule = MCFGRule.from_string('A(w1u, x1v) -> B(w1, x1) C(u, v)')
        inst1 = MCFGRuleElementInstance("B", (1, 2), (5, 7))
        inst2 =  MCFGRuleElementInstance("C", (2, 4), (7, 8))
        lhs_inst = rule.instantiate_left_side(inst1, inst2)
        assert lhs_inst.variable == "A"
        assert lhs_inst.string_spans == ((1, 4), (5, 8))

    def test_from_string(self):
        rule = MCFGRule.from_string("VP(uv) -> V(u) NP(v)")
        assert rule.left_side.variable == "VP"
        assert [e.variable for e in rule.right_side] == ["V", "NP"]

    def test_string_yield(self):
        rule = MCFGRule.from_string("D(the)")
        assert rule.string_yield() == "D"

    def test_string_yield_non_epsilon_raises(self):
        rule = MCFGRule.from_string("S(uv) -> NP(u) VP(v)")
        with pytest.raises(ValueError):
            rule.string_yield()

class TestMCFGGrammar:

    @pytest.fixture
    def grammar(self):
        rules = {
            MCFGRule.from_string("S(uv) -> NP(u) VP(v)"),
            MCFGRule.from_string("NP(uv) -> D(u) N(v)"),
            MCFGRule.from_string("D(the)"),
            MCFGRule.from_string("N(greyhound)")
        }
        alphabet = {"the", "greyhound"}
        variables = {"S", "NP", "VP", "D", "N"}
        return MCFGGrammar(alphabet, variables, rules, "S")

    def test_alphabet(self, grammar):
        assert grammar.alphabet == {"the", "greyhound"}

    def test_variables(self, grammar):
        assert "S" in grammar.variables
        assert "VP" in grammar.variables

    def test_start_variable(self, grammar):
        assert grammar.start_variable == "S"

    def test_rules(self, grammar):
        rules = grammar.rules
        assert any(r.left_side.variable == "S" for r in rules)

    def test_validate_alphabet_variable_overlap_raises(self):
        rules = {MCFGRule.from_string("X(uv) -> A(u) B(v)")}
        with pytest.raises(ValueError):
            MCFGGrammar({"X"}, {"X", "A", "B"}, rules, "X")

    def test_invalid_start_variable_raises(self):
        rules = {MCFGRule.from_string("X(uv) -> A(u) B(v)")}
        with pytest.raises(ValueError):
            MCFGGrammar({"a"}, {"X", "A", "B"}, rules, "Z")
