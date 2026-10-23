# ---------------------------------------------------------------
# FM-index with improvements: exact search of a pattern in a text
#
# Usage: python fm_index_improved.py <text> <pattern> <K>
#
# Improvement 1: SA without copying the suffixes. Only the positions are
#                sorted, comparing the suffixes on the original text.
# Improvement 2: checkpoints. occ is only stored every K rows and the rest
#                is computed by counting in L.
# ---------------------------------------------------------------
import sys
from functools import cmp_to_key


# --- 1. Build the index ---

# 1.1 Efficient suffix array (IMPROVEMENT 1: replaces suffixArray, which copied the suffixes)
def compareSuffixes(t, i, j):
    """ Decides which suffix goes first: the one starting at i or the one starting at j.
        Returns -1 if the one at i goes first, 1 if it goes after, 0 if they are the same. """
    if i == j:
        return 0
    while t[i] == t[j]:  # skip the common prefix
        i += 1
        j += 1
    # This never goes past the end: the $ is unique and last,
    # so two different suffixes differ at the $ at the latest
    if t[i] < t[j]:
        return -1
    return 1

def suffixArrayEfficient(t):
    """ SA: sa[row] = position in the text where the suffix of that row starts """
    def compare(i, j):  # sorted only passes i and j, so the text is fixed here
        return compareSuffixes(t, i, j)
    # cmp_to_key adapts a two-element comparison function so sorted can use it
    return sorted(range(len(t)), key=cmp_to_key(compare))

# 1.2 BWT (same as the basic version)
def bwtViaSa(t, sa):
    """ BWT (column L) from the SA, without building the BWM """
    bw = []
    for si in sa:
        if si == 0: bw.append('$')  # the suffix at 0 is the whole text -> its rotation ends in $
        else: bw.append(t[si-1])  # the letter just before each suffix
    return ''.join(bw)

# 1.3 Column F (same as the basic version)
def countLetters(bw):
    """ tots: how many times each letter appears in the BWT """
    tots = dict()
    for c in bw:
        if c not in tots:
            tots[c] = 0
        tots[c] += 1
    return tots

def firstCol(tots):
    """ first (column F): for each letter, its row range [start, end) """
    first = {}
    totc = 0
    for c, count in sorted(tots.items()):  # alphabetical order, as in F
        first[c] = (totc, totc + count)  # each block starts where the previous one ended
        totc += count
    return first

# 1.4 Checkpoints (IMPROVEMENT 2: replaces occTable, which stored every row)
def checkpointTable(bw, k):
    """ occ stored only at rows 0, k, 2k, ...  ->  cp[j] = occ of row j*k """
    counts = {}
    for c in sorted(set(bw)):
        counts[c] = 0
    cp = []
    for row in range(len(bw)):
        if row % k == 0:
            cp.append(dict(counts))  # a copy, so later rows do not change it
        counts[bw[row]] += 1
    # The search can ask for occ of row n (end of the range);
    # if n is a multiple of k, that checkpoint is still missing
    if len(bw) % k == 0:
        cp.append(dict(counts))
    return cp

def countOcc(cp, bw, k, row, c):
    """ occ[row][c] = how many c there are in L above the row (not counting it),
        computed from the closest checkpoint above """
    j = row // k
    total = cp[j][c]
    for i in range(j * k, row):  # at most k-1 rows; none if the row is a checkpoint
        if bw[i] == c:
            total += 1
    return total


# --- 2. Search ---

def backwardSearch(pattern, first, cp, bw, k):
    """ Range (start, end) of BWM rows that start with the pattern """
    # Start with the range of the last letter in F
    c = pattern[-1]
    if c not in first:
        return 0, 0
    start, end = first[c]

    # Then the rest of the letters, from right to left
    for c in reversed(pattern[:-1]):
        if c not in first:
            return 0, 0
        # LF-mapping on both borders, with occ computed from the checkpoints
        start = first[c][0] + countOcc(cp, bw, k, start, c)
        end = first[c][0] + countOcc(cp, bw, k, end, c)
        if start >= end:  # no c in L within the range
            return 0, 0
    return start, end  # end - start = number of occurrences


# --- 3. Locate ---

def locate(pattern, first, cp, bw, k, sa):
    """ Positions in the text where the pattern starts """
    start, end = backwardSearch(pattern, first, cp, bw, k)
    positions = []
    for row in range(start, end):
        positions.append(sa[row])  # the SA translates row -> position in the text
    return sorted(positions)


# --- 4. Main program ---

def main():
    if len(sys.argv) != 4:
        print("Usage: python fm_index_improved.py <text> <pattern> <K>")
        sys.exit(1)
    text = sys.argv[1]
    pattern = sys.argv[2]

    if not sys.argv[3].isdigit() or int(sys.argv[3]) < 1:
        print("Error: K must be an integer greater than or equal to 1")
        sys.exit(1)
    k = int(sys.argv[3])

    if pattern == "":
        print("Error: the pattern cannot be empty")
        sys.exit(1)
    if '$' in text:  # the $ must be unique, otherwise LF-mapping does not work
        print("Error: the text cannot contain '$' (it is used as the end marker)")
        sys.exit(1)
    text = text + "$"

    sa = suffixArrayEfficient(text)
    bw = bwtViaSa(text, sa)
    first = firstCol(countLetters(bw))
    cp = checkpointTable(bw, k)

    positions = locate(pattern, first, cp, bw, k, sa)

    print("Text:       ", text)
    print("BWT:        ", bw)
    print("Pattern:    ", pattern)
    print("K:          ", k, "(one checkpoint every", k, "rows)")
    print("Occurrences:", len(positions))
    print("Positions:  ", positions)


if __name__ == "__main__":  # only runs when executed directly, not when imported
    main()
