from Language_processing import langProc
from Tables import Base
from typing import List


class PatternMember:
    def __init__(self, _internals):
        self.internals: dict = _internals

    def check(self, word: str):
        ok = True
        for p, value in self.internals.items():
            if p == "is":
                if langProc.get_normal_from(word) != value:
                    ok = False
            elif p == "from":
                pathh = value.split('.')
                if len(pathh) == 1:
                    words = {item for sublist in Base[pathh[0]].values() for item in
                             sublist.split(', ')}
                else:
                    words = {item for item in Base[pathh[0]][pathh[1]].split(', ')}
                if word not in words:
                    ok = False
            elif p == "from_norm":
                pathh = value.split('.')
                if len(pathh) == 1:
                    words = {langProc.get_normal_from(item) for sublist in Base[pathh[0]].values() for item in
                             sublist.split(', ')}
                else:
                    words = {langProc.get_normal_from(item) for item in Base[pathh[0]][pathh[1]].split(', ')}
                if langProc.get_normal_from(word) not in words:
                    ok = False
            else:
                if not langProc.check_tag(word, value):
                    ok = False
        return ok


class PatternDist:
    def __init__(self, left_=3, right_=3):
        self.left = left_
        self.right = right_


class Pattern:
    def __init__(self, pattern_members: List[PatternMember], pattern_dists: List[PatternDist]):
        if len(pattern_dists) + 1 != len(pattern_members):
            raise ValueError
        self.pattern_members = pattern_members
        self.pattern_dists = pattern_dists

    def check(self, block: str) -> bool:
        words = langProc.get_words(block)
        d = [set() for _ in range(len(words))]
        for i, word in enumerate(words):
            for j, pat in enumerate(self.pattern_members):
                if pat.check(word):
                    d[i].add(j)
        found = False
        for i in range(len(words)):
            if 0 not in d[i]:
                continue
            fl = True
            for j in range(1, len(self.pattern_members)):
                fll = False
                for k in range(max(0, i - self.pattern_dists[j - 1].left),
                               min(len(words), i + self.pattern_dists[j - 1].right + 1)):
                    if j in d[k]:
                        fll = True
                        break
                if not fll:
                    fl = False
                    break
            if fl:
                return True
        return False


Patterns = {
    "future hopes": [Pattern([PatternMember({"from": "main_noun.self"}), PatternMember({"from": "hopes.verbs"}),
                              PatternMember({"is": "бы"})], [PatternDist(3, 3), PatternDist(1, 2)]),
                     Pattern([PatternMember({"from": "main_noun.self"}),
                              PatternMember({"from_norm": "hopes.future", "tense": "pres"})],
                             [PatternDist(0, 3)]),
                     Pattern([PatternMember({"from": "main_noun.self"}),
                              PatternMember({"tense": "futr"})],
                             [PatternDist(0, 3)]),
                     ],
    "past regrets": [Pattern([PatternMember({"from": "regrets.con"})], [])],
    "confidence": [Pattern([PatternMember({"from": "introductory.confidence_pos"})], []),
                   Pattern([PatternMember({"from": "introductory.confidence_neg"})], []),
                   Pattern([PatternMember({"from": "confidence.adverb"}), PatternMember({"from": "confidence.verbs"})],
                           [PatternDist(0, 1)]),
                   Pattern([PatternMember({"from": "confidence.adverb"}), PatternMember({"verb": "INFN"})],
                           [PatternDist(0, 1)]),
                   Pattern([PatternMember({"from": "confidence.colloc"})],
                           []),
                   ],
    "questions": [Pattern([PatternMember({"from": "subordinating_union"}), PatternMember({"from": "question_markers"})],
                          [PatternDist(0, 1)]),
                  Pattern([PatternMember({"from": "question_markers.politeness"})], [])],
    "cans": [Pattern([PatternMember({"from": "main_noun.self"}), PatternMember({"like": "ADJF"})], [PatternDist(0, 1)]),
             Pattern([PatternMember({"from": "can_like.neg"}), PatternMember({"from": "can_like.verbs"})],
                     [PatternDist(0, 3)]),
             Pattern([PatternMember({"from": "can_like.verbs"})], [])]
}
