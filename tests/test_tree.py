import pytest
from agenda_based_mcfg_wchoi18.tree import Tree # type: ignore

class TestTree:

    @pytest.fixture
    def sample_tree(self):
        return Tree("S", [
            Tree("NP", [Tree("D", [Tree("the")]), Tree("N", [Tree("greyhound")])]),
            Tree("VP", [Tree("V", [Tree("believed")]), Tree("NP", [Tree("D", [Tree("the")]), Tree("N", [Tree("human")])])])
        ])

    def test_str(self, sample_tree):
        assert str(sample_tree) == "the greyhound believed the human"

    def test_terminals(self, sample_tree):
        assert sample_tree.terminals == ["the", "greyhound", "believed", "the", "human"]

    def test_nonterminals(self, sample_tree):
        nts = sample_tree.nonterminals
        assert "S" in nts and "NP" in nts and "VP" in nts

    def test_eq_and_hash(self, sample_tree):
        same_tree = Tree("S", [
            Tree("NP", [Tree("D", [Tree("the")]), Tree("N", [Tree("greyhound")])]),
            Tree("VP", [Tree("V", [Tree("believed")]), Tree("NP", [Tree("D", [Tree("the")]), Tree("N", [Tree("human")])])])
        ])
        assert sample_tree == same_tree
        assert hash(sample_tree) == hash(same_tree)

    def test__validate(self):
        with pytest.raises(TypeError):
            Tree("X", ["not_a_tree"])

    def test_index(self, sample_tree):
        indices = sample_tree.index("NP")
        assert indices == [(0,), (1, 1)]

    def test_relabel_terminals(self, sample_tree):
        relabeled = sample_tree.relabel(lambda x: x.upper(), terminals_only=True)
        assert "THE" in relabeled.terminals

    def test_relabel_nonterminals(self, sample_tree):
        relabeled = sample_tree.relabel(lambda x: x + "_X", nonterminals_only=True)
        assert any(nt.endswith("_X") for nt in relabeled.nonterminals)

    def test_to_tuple_and_from_list(self):
        t = Tree("A", [Tree("B"), Tree("C")])
        tpl = t.to_tuple()
        assert tpl == ("A", (("B", ()), ("C", ())))
        restored = Tree.from_list(["A", ["B"], ["C"]])
        assert restored.to_tuple() == tpl

