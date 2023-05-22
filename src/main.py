import pymorphy2
import re
from typing import List, Tuple
from Tables import Base
from questions_patterns import active, reflex
from Pattern import Patterns, Pattern
from Language_processing import langProc


def process_text(ind_: int, text: str) -> Tuple[int, int, int, int]:
    a_t, r_t = 0, 0
    cnt = 0
    blocks = langProc.get_blocks_smart(text)
    for block in blocks:
        for part in block:
            for key, ind in active[ind_]:
                pattern: Pattern = Patterns[key][ind]
                if pattern.check(part):
                    a_t += 1
                    print("active", key, ind, part)
            for key, ind in reflex[ind_]:
                pattern: Pattern = Patterns[key][ind]
                if pattern.check(part):
                    r_t += 1
                    print("reflex", key, ind, part)
            cnt += langProc.count_nouns(part)
        if len(block) > 2:
            r_t += 1

    cnt /= len(blocks)
    if cnt > 5:
        r_t += 1
    else:
        a_t += 1
    if len(blocks) >= 4:
        a_t += 1
    elif len(blocks) <= 2:
        r_t += 1
    return a_t, r_t, len(blocks) + 2, len(blocks) + 2


morph = pymorphy2.MorphAnalyzer()
f = open("test.txt", "r")
text = ''.join(f.readlines())
text = text.replace("\n", "")
text = text.lower()
responses = re.split(r"(###\d+)", text)[1:]
a, r = 0, 0
max_a, max_r = 0, 0
for i in range(len(responses) // 2):
    ind = responses[i * 2]
    txt = responses[i * 2 + 1]
    at, rt, mat, mrt = process_text(int(ind[3:]) - 1, txt)
    a += at
    r += rt
    max_a += mat
    max_r += mrt
print("{}% active, {}% reflective".format(round(a / max_a * 100, 2), round(r / max_r * 100, 2)))
