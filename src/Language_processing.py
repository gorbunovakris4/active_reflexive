import pymorphy2
import re
from Tables import Base
from typing import List


class LangProc:
    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()

    @staticmethod
    def remove_sym(s: str) -> str:
        while len(s) > 0 and not s[0].isalpha():
            s = s[1:]
        while len(s) > 0 and not s[-1].isalpha():
            s = s[:len(s) - 1]
        return s

    def get_normal_from(self, word: str) -> str:
        return self.morph.parse(word)[0].normal_form

    def get_grammem(self, word: str) -> str:
        return str(self.morph.parse(word)[0].tag).split(',')[0].split(' ')[0]

    def is_prt(self, word: str) -> bool:
        return self.get_grammem(word) in ["PRTF", "PRTS", "GRND"]

    @staticmethod
    def get_words(text: str) -> List[str]:
        return re.findall(r'[А-я]+', text)

    @staticmethod
    def get_sentences(text: str) -> List[str]:
        return re.split(r'[\.!\?]+', text)

    def has_prt(self, sentence: str) -> bool:
        for word in self.get_words(sentence):
            if self.is_prt(word):
                return True
        return False

    def check_tag(self, word: str, value: str) -> bool:
        return value in self.morph.parse(word)[0].tag

    def count_nouns(self, text: str) -> int:
        cnt = 0
        for word in self.get_words(text):
            if self.get_grammem(word) not in ["PREP", "CONJ", "PRCL", "INTJ"]:
                cnt += 1
        return cnt

    def get_blocks_smart(self, text: str) -> List[List[str]]:
        sentences = self.get_sentences(text)
        res = []
        for sentence in sentences:
            blocks = []
            prev_block = []
            flag = False
            for block in sentence.split(","):
                if re.search(
                        r'(\s|$|,)|(\s|^)'.join(
                            r'(\s|$|,)|(\s|^)'.join(Base["subordinating_union"].values()).split(", ")),
                        block) is not None:
                    if len(blocks) > 0:
                        prev_block.append(blocks[-1])
                        blocks.pop()
                        flag = True
                elif re.search(
                        r'(\s|$|,)|(\s|^)'.join(r'(\s|$|,)|(\s|^)'.join(Base["introductory"].values()).split(", ")),
                        block) is not None:
                    if len(blocks) > 0:
                        prev_block.append(blocks[-1])
                        blocks.pop()
                        flag = True
                elif self.has_prt(block):
                    if len(blocks) > 0:
                        prev_block.append(blocks[-1])
                        blocks.pop()
                        flag = True
                elif re.search(r'(\s|^)' + r'(\s|$|,)|(\s|^)'.join(
                        r'(\s|$|,)|(\s|^)'.join(Base["coordinative_union"].values()).split(", ")) + r'(\s|$|,)',
                               block) is not None or not flag:
                    if len(blocks) > 0:
                        block = blocks[-1] + block
                        blocks.pop()
                elif flag:
                    block = prev_block[-1] + block
                    prev_block.pop()
                    flag = False
                block = block.strip()
                if block != "":
                    blocks.append(block)
            while len(prev_block) > 0:
                blocks.append(prev_block[-1])
                prev_block.pop()
            res.append(blocks)
        return res


langProc = LangProc()
