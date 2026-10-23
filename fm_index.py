# ---------------------------------------------------------------
# FM-index: exact search of a pattern in a text
# Usage: python fm_index.py <text> <pattern>
# ---------------------------------------------------------------
import sys

# --- 1. Build the index ---

# 1.1 Suffix array (adapted from the course slides)
def suffixArray(s):
    """ SA: sa[row] = position in the text where the suffix of that row starts """
    satups = sorted([(s[i:], i) for i in range(0, len(s))])  # (suffix, position) pairs sorted by suffix
    sa = []
    for suffix, position in satups:
        sa.append(position)
    return sa

# 1.2 BWT (adapted from the course slides)
def bwtViaSa(t, sa):
    """ BWT (column L) from the SA, without building the BWM """
    bw = []
    for si in sa:
        if si == 0: bw.append('$')  # the suffix at 0 is the whole text -> its rotation ends in $
        else: bw.append(t[si-1])  # the letter just before each suffix
    return ''.join(bw)

# 1.3 Column F
def countLetters(bw):
    """ tots: how many times each letter appears in the BWT """
    tots = dict()
    for c in bw:
        if c not in tots:
            tots[c] = 0
        tots[c] += 1
    return tots

def firstCol(tots): # (adapted from the course slides)
    """ first (column F): for each letter, its row range [start, end) """
    first = {}
    totc = 0
    for c, count in sorted(tots.items()):  # alphabetical order, as in F
        first[c] = (totc, totc + count)  # each block starts where the previous one ended
        totc += count
    return first

# 1.4 occ table
def occTable(bw):
    """ occ[i][c] = how many c there are in L above row i (not counting it) """
    counts = {}
    for c in sorted(set(bw)):
        counts[c] = 0
    occ = []  # list of dictionaries: occ[row][letter]
    for c in bw:
        occ.append(dict(counts))  # a copy, so later rows do not change it
        counts[c] += 1
    occ.append(dict(counts))  # extra row with the total: in the search, end can be len(bw)
    return occ


# --- 2. Search ---

def backwardSearch(pattern, first, occ):
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
        # LF-mapping on both borders: the c's of L within the range, placed in F
        start = first[c][0] + occ[start][c]
        end = first[c][0] + occ[end][c]
        if start >= end:  # no c in L within the range
            return 0, 0
    return start, end  # end - start = number of occurrences


# --- 3. Locate ---

def locate(pattern, first, occ, sa):
    """ Positions in the text where the pattern starts """
    start, end = backwardSearch(pattern, first, occ)
    positions = []
    for row in range(start, end):
        positions.append(sa[row])  # the SA translates row -> position in the text
    return sorted(positions)


# --- 4. Main program ---

def main():
    if len(sys.argv) != 3:
        print("Usage: python fm_index.py <text> <pattern>")
        sys.exit(1)
    text = sys.argv[1]
    pattern = sys.argv[2]

    if pattern == "":
        print("Error: the pattern cannot be empty")
        sys.exit(1)
    if '$' in text:  # the $ must be unique, otherwise LF-mapping does not work
        print("Error: the text cannot contain '$' (it is used as the end marker)")
        sys.exit(1)
    text = text + "$"

    sa = suffixArray(text)
    bw = bwtViaSa(text, sa)
    first = firstCol(countLetters(bw))
    occ = occTable(bw)

    positions = locate(pattern, first, occ, sa)

    print("Text:       ", text)
    print("BWT:        ", bw)
    print("Pattern:    ", pattern)
    print("Occurrences:", len(positions))
    print("Positions:  ", positions)


if __name__ == "__main__":  # only runs when executed directly, not when imported
    main()
