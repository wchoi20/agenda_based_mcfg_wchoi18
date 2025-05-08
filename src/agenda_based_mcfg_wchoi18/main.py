from agenda_based_mcfg_wchoi18.grammar import MCFGGrammar, MCFGRule, MCFGRuleElement
from agenda_based_mcfg_wchoi18.parser import AgendaBasedMCFGParser
from agenda_based_mcfg_wchoi18.tree import Tree

import re

TEST_RULES = """
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

def main():
    rules = [MCFGRule.from_string(line.strip()) for line in TEST_RULES.splitlines() if '(' in line]
    grammar = MCFGGrammar(alphabet={'which', 'who', 'the', 'a', 'greyhound', 'human', 
                                    'believes', 'believe', 'does', 'that'},
                             variables={'S', 'Sbar', 'Sbarwh', 'Swhmain', 'Swhemb', 
                                        'Src', 'Swhrc', 'VP', 'VPwhmain', 'VPwhemb', 
                                        'VPrc', 'VPwhrc', 'NP', 'NPdisloc', 'NPwh', 'Nrc'},
                             rules=rules,
                             start_variable='S')

    parser = AgendaBasedMCFGParser(grammar)
    tokens = ["who", "does", "the", "greyhound", "believe"]
    results = parser.parse(tokens)

    print(f"Parsed {len(results)} result(s)")
    for tree in results:
        print(tree.to_string())

if __name__ == "__main__":
    main()
