# FM-index in Python

A simple implementation of the **FM-index** to find every position where a pattern appears in a text.

## What is an FM-index?

Searching for a pattern by reading the whole text every time is slow when the text is long (for example, a genome with millions of letters). An FM-index is a structure built **once** from the text that lets you count and locate any pattern in a time that depends on the **length of the pattern**, not the length of the text.

It is used in bioinformatics to align millions of short DNA reads against a reference genome. Tools like Bowtie and BWA are built on it.

## How it works

1. **Build the index** from the text (a `$` is added at the end to mark it):
   - **Suffix array (SA):** the positions of all the suffixes of the text, sorted alphabetically.
   - **BWT (column L):** for each suffix in that order, the letter just before it. It is a rearrangement of the text where equal letters tend to group together.
   - **Column F:** for each letter, the block of rows it occupies in the sorted order. Only the start and end of each block is stored.
   - **occ table:** for each row of L, how many of each letter there are above it.
2. **Search (backward search):** the pattern is read from right to left. It starts with the rows of its last letter and, for each previous letter, narrows the range using F and occ (LF-mapping). Each letter only needs two lookups in occ. The size of the final range is the number of occurrences.
3. **Locate:** the suffix array turns each row of the final range into a position in the text.

Example: in `abaaba`, the pattern `aba` appears at positions 0 and 3.

## Files

- `fm_index.py`: basic version.
- `fm_index_improved.py`: the same with two improvements to use less memory:
  1. **Suffix array without copying the suffixes.** The basic version copies every suffix to sort them (about n²/2 letters for a text of length n). Here only the positions are sorted, comparing the suffixes letter by letter on the original text, so it only stores n numbers.
  2. **Checkpoints.** Instead of storing the occ table for every row, it is only stored every K rows. The missing rows are computed by counting at most K − 1 letters in L. A small K uses more memory and searches faster; a large K uses less memory and searches more slowly. The result is the same for any K.

## Usage

Requires Python 3, no extra libraries.

```
python fm_index.py <text> <pattern>
python fm_index_improved.py <text> <pattern> <K>
```

Examples:

```
$ python fm_index.py abaaba aba
Text:        abaaba$
BWT:         abba$aa
Pattern:     aba
Occurrences: 2
Positions:   [0, 3]

$ python fm_index_improved.py TTATTTATGATTATTATC TTA 2
Text:        TTATTTATGATTATTATC$
BWT:         CTTTGTTTTTTTAAATA$A
Pattern:     TTA
K:           2 (one checkpoint every 2 rows)
Occurrences: 4
Positions:   [0, 4, 10, 13]
```

- If the text or the pattern contain spaces, put them in quotes.
- The text cannot contain `$`, because the program adds it at the end.
- K must be an integer greater than or equal to 1.

## Context and credits

Assignment for the course *Procesamiento avanzado de secuencias biológicas* (2026/2027). `suffixArray`, `bwtViaSa` and `firstCol` are adapted from the course slides (based on Ben Langmead's teaching material). The rest is my own work.
