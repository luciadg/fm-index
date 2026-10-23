# ---------------------------------------------------------------
# Tests: the basic version, the improved version and a simple search
# must give the same positions
# Usage: python test.py
# ---------------------------------------------------------------
import fm_index
import fm_index_improved

K = 2


def simpleSearch(text, pattern):
    """ Tries every position of the text """
    positions = []
    for i in range(len(text) - len(pattern) + 1):
        if text[i:i + len(pattern)] == pattern:
            positions.append(i)
    return positions


def searchBasic(text, pattern):
    t = text + "$"
    sa = fm_index.suffixArray(t)
    bw = fm_index.bwtViaSa(t, sa)
    first = fm_index.firstCol(fm_index.countLetters(bw))
    occ = fm_index.occTable(bw)
    return fm_index.locate(pattern, first, occ, sa)


def searchImproved(text, pattern):
    t = text + "$"
    sa = fm_index_improved.suffixArrayEfficient(t)
    bw = fm_index_improved.bwtViaSa(t, sa)
    first = fm_index_improved.firstCol(fm_index_improved.countLetters(bw))
    cp = fm_index_improved.checkpointTable(bw, K)
    return fm_index_improved.locate(pattern, first, cp, bw, K, sa)


def main():
    tests = [("abaaba", "aba"), ("banana", "ana"), ("abaaba", "bb"),
             ("TTATTTATGATTATTATC", "TTA"), ("hola mundo hola", "hola")]

    for text, pattern in tests:
        simple = simpleSearch(text, pattern)
        basic = searchBasic(text, pattern)
        improved = searchImproved(text, pattern)
        if simple == basic == improved:
            print("OK  ", text, pattern, simple)
        else:
            print("FAIL", text, pattern, simple, basic, improved)


if __name__ == "__main__":
    main()
