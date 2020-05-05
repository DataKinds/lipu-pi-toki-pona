from tqdm import tqdm
import math

EPSILON = 0.01

def longest_common_subsequence(w1, w2):
    w1, w2 = max(w1, w2), min(w1, w2)
    if len(w1) == 0:
        return 0

    if len(w1) == 1:
        if len(w2) == 0:
            return 0
        return w1[0] == w2[0]

    dp = [[0 for j in range(len(w2) + 1)] for i in range(len(w1) + 1)]
    # dp[i][j] = lcs(w1[:i], w2[:j])

    for i, c1 in enumerate(w1):
        for j, c2 in enumerate(w2):
            if c1 == c2:
                dp[i][j] = max(dp[i - 1][j - 1] + 1, dp[i][j])
            else:
                dp[i][j] = max(dp[i][j], dp[i - 1][j], dp[i][j - 1])

    return dp[-2][-2]

class Word:
    def __init__(self, word, vector):
        self.word = word
        self.vector = vector

    def __str__(self):
        return f"Word({repr(self.word)})"

    def get_factor(self, other):
        # The words need to start with the same letters and length differ by at most 20%
        if self.word[0] != other[0]:
            return 0
        len_ratio = len(self.word) / len(other)
        len_ratio = max(len_ratio, 1 / len_ratio)

        if len_ratio > 1.7:
            return 0

        lcs_ratio = longest_common_subsequence(self.word, other) / max(len(self.word), len(other))

        return lcs_ratio ** 20

given = "dictionaries"
words = open("/usr/share/dict/words").read().strip().split("\n")

facs = {}

for word in tqdm(words):
    wword = Word(word, None)

    fac = wword.get_factor(given)
    if fac != 0:
        facs[word] = fac

total_fac = sum(facs.values())

for word in sorted(facs.keys(), key=lambda word: facs[word], reverse=True)[:20]:
    print(f"{word}: {facs[word] / total_fac} ({facs[word]})")
