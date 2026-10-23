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
from functools import cmp_to_key  # improvement 1 (Python standard library)


# --- 1. Build the index ---
# IMPROVEMENT 1: replaces suffixArray, which copied the suffixes with s[i:]
# 1.1 Efficient suffix array
def compareSuffixes(t, i, j):  # the goal is to sort suffixes, so it compares letters (i and j)
    """ Decides which suffix goes first: the one starting at position i
        or the one starting at position j.
        Returns -1 if the one at i goes first, 1 if it goes after, 0 if they are the same. """
    if i == j:
        return 0  # same position = same suffix
    while t[i] == t[j]:  # if the letters are equal, move on to the next position to compare lexicographically
        i += 1
        j += 1
    # We always get here without going past the text: the $ is unique and at the
    # end, so two different suffixes differ at the $ at the latest
    if t[i] < t[j]:
        return -1  # the suffix at i goes first
    return 1  # the suffix at j goes first

def suffixArrayEfficient(t):
    """ SA: sa[row] = position in the text where the suffix of that row starts """
    def compare(i, j):  # compareSuffixes with the text already set (sorted only passes i, j)
        return compareSuffixes(t, i, j)
    positions = range(len(t))  # 0, 1, ... n-1: just numbers, no suffix copied
    return sorted(positions, key=cmp_to_key(compare))  # cmp_to_key: in Python 3 sorted does not accept a function that compares two elements, this adapts it

# 1.2 BWT (same as before)
def bwtViaSa(t, sa):
    """ BWT (column L) from the SA, without building the BWM """
    bw = []
    for si in sa:
        if si == 0: bw.append('$')  # the suffix starting at 0 is the whole text -> the $ goes before it (rotation)
        else: bw.append(t[si-1])  # the letter just before each suffix
    return ''.join(bw)  # from list to string

# 1.3 Column F (same as before)
def countLetters(bw):
    """ tots: how many times each letter appears in the BWT """
    tots = dict()
    for c in bw:
        if c not in tots:
            tots[c] = 0  # first time this letter shows up
        tots[c] += 1
    return tots


def firstCol(tots): # (same as before, the basic one)
    """ first (column F): for each letter, its row range [start, end) """
    first = {}
    totc = 0  # how many rows so far
    for c, count in sorted(tots.items()):  # in alphabetical order, as in F
        first[c] = (totc, totc + count)  # the block of c starts where the previous one ended
        totc += count
    return first

# IMPROVEMENT 2: replaces occTable, which stored every row
# 1.4 Checkpoints
def checkpointTable(bw, k):
    """ Checkpoints: occ stored only at rows 0, k, 2k, ...
        cp[j] = occ of row j*k """
    counts = {}
    for c in sorted(set(bw)):
        counts[c] = 0  # start with all of them at 0
    cp = []
    for row in range(len(bw)):  # go through L row by row
        if row % k == 0:  # if it is a multiple of k, store the counts before this row
            cp.append(dict(counts)) # dict(...) makes a copy; otherwise all checkpoints would be the same dictionary and change together
        counts[bw[row]] += 1  # add the letter of this row (always, stored or not)
    if len(bw) % k == 0:  # backwardSearch can ask for occ of row n (the end of the range); if n is a multiple of k, that checkpoint has not been stored yet
        cp.append(dict(counts))
    return cp

def countOcc(cp, bw, k, row, c):
    """ occ[row][c] = how many c there are in L above the row (not counting it),
        computed with the checkpoints """
    j = row // k  # number of the checkpoint above (integer division)
    total = cp[j][c]  # the stored value
    for i in range(j * k, row):  # from that checkpoint up to before the row (at most k-1 rows; if the row is a checkpoint, it does not run at all)
        if bw[i] == c:  # count the c's in L
            total += 1
    return total


# --- 2. Search ---

def backwardSearch(pattern, first, cp, bw, k):
    """ Range (start, end) of BWM rows that start with the pattern """
    # Step 1: last letter of the pattern -> its range in F
    c = pattern[-1]  # pattern[-1] = the last letter
    if c not in first:
        return 0, 0  # that letter is not in the text -> 0 occurrences
    start, end = first[c]  # its range in F, e.g. first['a'] = (1, 5)

    # Step 2: the rest of the letters, from right to left
    # pattern[:-1] = the pattern without its last letter (already used above)
    # reversed(...) = go through it backwards
    for c in reversed(pattern[:-1]):
        if c not in first:
            return 0, 0  # letter not in the text
        # LF-mapping on both borders (improvement 2: occ computed with countOcc)
        start = first[c][0] + countOcc(cp, bw, k, start, c)  # where the c's start in F + c's above the range
        end = first[c][0] + countOcc(cp, bw, k, end, c)  # where the c's start in F + c's up to the end of the range
        # Step 3: empty range -> there was no c in L within the range
        if start >= end:
            return 0, 0
    return start, end  # rows that start with the pattern; end - start = number of occurrences


# --- 3. Locate ---

def locate(pattern, first, cp, bw, k, sa):
    """ Positions in the text where the pattern starts """
    start, end = backwardSearch(pattern, first, cp, bw, k)  # BWM rows that start with the pattern
    positions = []
    for row in range(start, end):  # each row of the range (end not included)
        positions.append(sa[row])  # the SA translates row -> position in the text
    return sorted(positions)  # sorted from lowest to highest, easier to read


# --- 4. Read text, pattern and K ---

if len(sys.argv) != 4:  # program name + text + pattern + K
    print("Usage: python fm_index_improved.py <text> <pattern> <K>")
    sys.exit(1)
text = sys.argv[1]
pattern = sys.argv[2]

if not sys.argv[3].isdigit() or int(sys.argv[3]) < 1:  # isdigit: is it all digits?
    print("Error: K must be an integer greater than or equal to 1")
    sys.exit(1)
K = int(sys.argv[3])  # improvement 2: every how many rows a checkpoint is stored (sys.argv gives text, int turns it into a number)

if '$' in text:  # the $ must be unique: if it appears inside the text, LF-mapping does not work
    print("Error: the text cannot contain '$' (it is used as the end marker)")
    sys.exit(1)
text = text + "$"  # marks the end of the text


# --- 5. Build the index, search and print ---

sa = suffixArrayEfficient(text)  # improvement 1
bw = bwtViaSa(text, sa)
first = firstCol(countLetters(bw))
cp = checkpointTable(bw, K)  # improvement 2

positions = locate(pattern, first, cp, bw, K, sa)

print("Text:       ", text)
print("BWT:        ", bw)
print("Pattern:    ", pattern)
print("K:          ", K, "(one checkpoint every", K, "rows)")
print("Occurrences:", len(positions))
print("Positions:  ", positions)
