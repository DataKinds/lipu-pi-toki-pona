from tqdm import tqdm
import math
import w2v_loader
import numpy as np

WORD_LIMIT = 250000


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

    def get_ext(self):
        return "_".join(self.word.split("_")[1:])

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

    f = w2v_loader.get_or_load_model(mode="r")

    DIMS = int(next(f).split()[1])

    with tqdm(total=WORD_LIMIT, unit="line", unit_scale=True) as prog:
        for line in f:
            line = line.strip()
            if line == "":
                continue

            prog.update(1)

            if len(words) > WORD_LIMIT:
                break

            word, *vector = line.split()
            if not "_NOUN" in word and not "_ADJ" in word and not "_VERB" in word:
                continue

            if DIMS != len(vector):
                print(f"Expected {DIMS} dims, got {line}")
                exit()

            wword = Word(word, [float(v) for v in vector])
            words.append(wword)

    return words, DIMS

def get_string_vector(words, string, verbose=False):
    if verbose:
        words = tqdm(words)

    facs = {}
    for word in words:
        fac = word.get_factor(string)
        if fac != 0:
            facs[word] = fac

    if len(facs) == 0:
        return None

    total_fac = sum(facs.values())

    if verbose:
        for word in sorted(facs.keys(), key=lambda word: facs[word], reverse=True)[:10]:
            print(f"{word}: {facs[word] / total_fac:.5} ({facs[word]:.5})")

    vector_total = None

    for word, fac in facs.items():
        if vector_total is None:
            vector_total = np.zeros_like(word.vector)
        vector_total += np.array(word.vector) * fac

    vector_avg = vector_total / total_fac

    return vector_avg

def load_tp_words(words):
    tp_words = []
    for cont in tqdm(open("nimi-ale-pona.txt", "r").read().split("\n\n")):
        if "\t" not in cont:
            continue
        word, descs = cont.split("\t")
        word = word.strip()
        for line in descs.split("\n"):
            line = line.strip()
            word_type, *sim = line.split("   ")
            sim = " ".join(sim)
            sim_words = "".join([ch if ch.isalnum() else " " for ch in sim]).split()
            sim_words = [word for word in sim_words if word.strip() != ""]

            vectors = [get_string_vector(words, word) for word in sim_words]
            vectors = [v for v in vectors if v is not None]

            if len(vectors) > 0:
                avg_vec = sum(vectors) / len(vectors)

                tp_words.append(Word(word + "_" + word_type, avg_vec))

    return tp_words

if __name__ == "__main__":
    words, DIMS = load_words()

    tp_words = load_tp_words(words)

    while True:
        string = input("> ").strip()
        vec = get_string_vector(words, string, verbose=True)

        if vec is None:
            print("Word not found!")
            continue

        angles = [(word, word.angle_to(vec)) for word in tp_words]
        for (word, angle) in sorted(angles, key=lambda pair: pair[1])[:10]:
            print(f"{word.word}: {math.degrees(angle):.5}°")
