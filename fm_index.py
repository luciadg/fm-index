# ---------------------------------------------------------------
# FM-index: exact search of a pattern in a text
# Usage: python fm_index.py <text> <pattern>
# ---------------------------------------------------------------
import sys

# --- 1. Build the index ---

# 1.1 Suffix array (adapted from the course slides)
def suffixArray(s):
    """ SA: sa[row] = position in the text where the suffix of that row starts """
    satups = sorted([(s[i:], i) for i in range(0, len(s))])  # (suffix, position) pairs sorted alphabetically by suffix
    sa = []
    for suffix, position in satups:
        sa.append(position)  # keep only the position
    return sa

# 1.2 BWT (adapted from the course slides)
def bwtViaSa(t, sa):
    """ BWT (column L) from the SA, without building the BWM """
    bw = []
    for si in sa:
        if si == 0: bw.append('$')  # the suffix starting at 0 is the whole text -> the $ goes before it (rotation)
        else: bw.append(t[si-1])  # the letter just before each suffix
    return ''.join(bw)  # from list to string

# 1.3 Column F
def countLetters(bw):
    """ tots: how many times each letter appears in the BWT """
    tots = dict()
    for c in bw:
        if c not in tots:
            tots[c] = 0  # first time this letter shows up
        tots[c] += 1
    return tots

def firstCol(tots): # (adapted from the course slides)
    """ first (column F): for each letter, its row range [start, end) """
    first = {}
    totc = 0  # how many rows so far
    for c, count in sorted(tots.items()):  # in alphabetical order, as in F
        first[c] = (totc, totc + count)  # the block of c starts where the previous one ended
        totc += count
    return first

# 1.4 occ table
def occTable(bw):
    """ occ[i][c] = how many c there are in L above row i (not counting it) """
    letters = sorted(set(bw))  # distinct letters, e.g. ['$', 'a', 'b']
    counts = {}
    for c in letters:
        counts[c] = 0  # start with all of them at 0
    occ = []  # list of dictionaries: occ[row][letter]
    for c in bw:  # go through L row by row
        occ.append(dict(counts))  # store the counts before this row (a copy, not the same dictionary)
        counts[c] += 1  # and then add the letter of this row
    occ.append(dict(counts))  # extra row with the total (in the search, end can be len(bw))
    return occ


# --- 2. Search ---

def backwardSearch(pattern, first, occ):
    """ Range (start, end) of BWM rows that start with the pattern """
    # Step 1: last letter of the pattern -> its range in F
    c = pattern[-1]  # pattern[-1] = the last letter
    if c not in first:
        return 0, 0  # that letter is not in the text -> 0 occurrences
    start, end = first[c]  # its range in F, e.g. first['a'] = (1, 5)

    # Step 2: the rest of the letters, from right to left
    # pattern[:-1] = the pattern without its last letter (already used above)
    # reversed(...) = go through it backwards
    for c in reversed(pattern[:-1]): # next letter to the left: look for it in L within the current range
        if c not in first:
            return 0, 0  # letter not in the text
        # LF-mapping on both borders: the c's of L within the range, placed in F
        start = first[c][0] + occ[start][c]  # where the c's start in F + c's above the range
        end = first[c][0] + occ[end][c]  # where the c's start in F + c's up to the end of the range
        # Step 3: empty range -> there was no c in L within the range
        if start >= end:
            return 0, 0
    return start, end  # rows that start with the pattern; end - start = number of occurrences


# --- 3. Locate ---

def locate(pattern, first, occ, sa):
    """ Positions in the text where the pattern starts """
    start, end = backwardSearch(pattern, first, occ)  # range of rows that start with the pattern
    positions = []
    for row in range(start, end):  # each row of the range (end not included)
        positions.append(sa[row])  # the SA translates row -> position in the text
    return sorted(positions)  # sorted from lowest to highest, easier to read


# --- 4. Read text and pattern ---

if len(sys.argv) != 3:  # program name + text + pattern
    print("Usage: python fm_index.py <text> <pattern>")
    sys.exit(1)
text = sys.argv[1]
pattern = sys.argv[2]

if '$' in text:  # the $ must be unique: if it appears inside the text, LF-mapping does not work
    print("Error: the text cannot contain '$' (it is used as the end marker)")
    sys.exit(1)
text = text + "$"  # marks the end of the text


# --- 5. Build the index, search and print ---

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
