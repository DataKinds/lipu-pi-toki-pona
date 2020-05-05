from tqdm import tqdm
import math
import w2v_loader
import numpy as np

WORD_LIMIT = 25000


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
        self.vector = np.array(vector)

    def __str__(self):
        return f"Word({repr(self.word)})"

    def get_subword(self):
        return self.word.split("_")[0]

    def get_factor(self, other):
        # The words need to start with the same letters and length differ by at most 20%
        here = self.get_subword()

        if here[0] != other[0]:
            return 0
        len_ratio = len(here) / len(other)
        len_ratio = max(len_ratio, 1 / len_ratio)

        if len_ratio > 1.7:
            return 0

        lcs_ratio = longest_common_subsequence(here, other) / max(len(here), len(other))

        return lcs_ratio ** 20

    def angle_to(self, other_vector):
        # a * b = ||a|| ||b|| cos(alpha)
        # la
        # alpha = cos⁻¹(a * b / (||a|| ||b||))

        dot = self.vector.dot(other_vector)
        self_len_sqr = self.vector.dot(self.vector)
        other_len_sqr = other_vector.dot(other_vector)

        cosine = dot / ((self_len_sqr * other_len_sqr) ** 0.5)
        cosine = min(1, cosine)
        return math.acos(cosine)

def load_words():
    print("Loading words")
    words = []

    lines = w2v_loader.get_or_load_model(mode="r").readlines()
    DIMS = int(lines[0].split()[1])

    for line in tqdm(lines[1:]):
        line = line.strip()
        if line == "":
            continue

        if len(words) > WORD_LIMIT:
            break

        word, *vector = line.split()

        if DIMS != len(vector):
            print(f"Expected {DIMS} dims, got {line}")
            exit()

        wword = Word(word, [float(v) for v in vector])
        words.append(wword)

    return words, DIMS

def get_string_vector(words, string):

    facs = {}
    for word in tqdm(words):
        fac = word.get_factor(string)
        if fac != 0:
            facs[word] = fac

    total_fac = sum(facs.values())

    for word in sorted(facs.keys(), key=lambda word: facs[word], reverse=True)[:10]:
        print(f"{word}: {facs[word] / total_fac:.5} ({facs[word]:.5})")

    vector_total = np.zeros(DIMS)
    for word, fac in facs.items():
        vector_total += np.array(word.vector) * fac

    vector_avg = vector_total / total_fac

    return vector_avg


if __name__ == "__main__":
    words, DIMS = load_words()

    tp_words = []
    for cont in tqdm(open("nimi-ale-pona.txt", "r").read().split("\n\n")):
        if "–" not in cont:
            continue
        word, desc = cont.split("–")
        word = word.strip()
        desc = desc.strip()
        desc_words = "".join([ch if ch.isalnum() else " " for ch in desc]).split()
        desc_words = [word for word in desc_words if word.strip() != ""]

        matching_words = [word for word in words if word.get_subword() in desc_words]
        if len(matching_words) > 0:
            total_vec = sum(word.vector for word in matching_words)
            avg_vec = total_vec / len(matching_words)

            tp_words.append(Word(word, avg_vec))

    while True:
        string = input("> ").strip()
        vec = get_string_vector(words, string)

        angles = [(word, word.angle_to(vec)) for word in tp_words]
        for (word, angle) in sorted(angles, key=lambda pair: pair[1])[:10]:
            print(f"{word.word}: {math.degrees(angle)}°")
