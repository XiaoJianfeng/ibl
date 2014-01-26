#!/usr/bin/env python

import time
from functools import partial
# import os.path
# import numpy as np

"""
functions to iter over .fasta and .fastq files. and I believe fasta_iter and fastq_iter are faster than many iterators available.

created: long time ago
last modified: 2014.01.26 - use partial to read blocks from file
"""

#-----------------------------------------------------------------------------
def fasta_iter(f, blocksize=int(1e7)):
    """
    fasta generator
    a fasta record is a tuple of (name_line, seq)

    f:         a file name or a file object
    blocksize: the same as in file_block_iter
    """

    if isinstance(f, basestring):
        fobj = open(f, 'r')
    elif isinstance(f, file):
        fobj = f
    else:
        raise Exception("Invalid file: %s" % f)

    name_line, seq_lines = "", []
    # inspired by https://speakerdeck.com/pyconslides/transforming-code-into-beautiful-idiomatic-python-by-raymond-hettinger-1
    for block in iter(partial(fobj.readlines, blocksize), []):
        for line in block:
            if line.startswith(">"):
                if seq_lines:
                    yield (name_line, "".join(seq_lines))
                    seq_lines = []
                name_line = line
            else:
                seq_lines.append(line.strip())
    if seq_lines:
        yield (name_line, "".join(seq_lines))

def fastq_iter(f, blocksize=int(1e7)):
    """
    fastq generator
    a fastq record is a list of 4 lines

    f:         a file name or a file object
    blocksize: the same as in file_block_iter

    Note: "\n" at the end of each line are retained.
    """

    if isinstance(f, basestring):
        fobj = open(f, 'r')
    elif isinstance(f, file):
        fobj = f
    else:
        raise Exception("Invalid file: %s" % f)

    lines_left = []
    # inspired by https://speakerdeck.com/pyconslides/transforming-code-into-beautiful-idiomatic-python-by-raymond-hettinger-1
    for block in iter(partial(fobj.readlines, blocksize), []):
        if lines_left:  # add lines_left to the first of block
            block[:0] = lines_left
        n = len(block)
        if n%4 == 0:
            lines_left = []
        else:
            lines_left = block[-(n%4):]
        for i in range(n//4):
            yield block[i*4:i*4+4]
    # lines_left should have 4 or 0 lines
    if lines_left:
        if (len(lines_left) != 4):
            raise Exception("Error, the lines of the file should be 4*n!")
        yield lines_left

# #-----------------------------------------------------------------------------
# class Fastq:
#     def __init__(self, f):
#         if os.path.exists(f):
#             self.f = f
#         else:
#             raise Exception("file %s doesn't exists" % f)
#     def alphabet_frequency(self, baseonly=True):
#         pass
#     def alphabet_percycle(self, percent=False):
#         results = []
#         fq_generator = fastq_iter(self.f)
#         # lines generated with fastq_iter have "\n" at the end, so use .strip() to remove it
#         seqs = [fq[1].strip() for fq in islice(fq_generator, 0, 500000)] 
#         while seqs:
#             counts = izip_longest(*[[p.count(k) for k in "ATGCN"] for p in izip_longest(*seqs, fillvalue='')], fillvalue=0)
#             results.extend(counts)
#             seqs = [fq[1].strip() for fq in islice(fq_generator, 0, 500000)]
# 
#         results2 = np.array(list(izip_longest(*results, fillvalue=0)))
#         m = results2.shape[0]
#         n = len("ATGCN")
#         counts = np.zeros((m, n), dtype=np.int)
#         for i in range(n):
#             counts[:,i] = results2[:,i::n].sum(axis=1)
# 
#         if percent:
#             counts = counts*1.0/counts.sum(axis=1).reshape((counts.shape[0], 1))
#         return counts
# 
#     def dinucleotide_frequency(self):
#         pass
# 
#     def alphabet_percycle2(self, percent=False):
#         def func(fq_item):
#             seq = fq_item[1]
#             return [seq.count(k) for k in "ATGCN"]
#         return alphabet_percycle(fastq_iter(self.f), func, percent=percent)
# 
# 
# #-----------------------------------------------------------------------------
# class Fasta:
#     def __init__(self, f):
#         if os.path.exists(f):
#             self.f = f
#         else:
#             raise Exception("file %s doesn't exists" % f)
# 
#     def fasta_iter(self):
#         for fa in fasta_iter(self.f):
#             yield fa
# 
#     def _alphabet_percycle(self, percent=False):
#         seqs = [fa[1] for fa in fasta_iter(self.f)]
#         counts = np.array([[p.count(k) for k in "ATGCN"] for p in izip_longest(*seqs, fillvalue='')])
#         if percent:
#             counts = counts*1.0/counts.sum(axis=1).reshape((counts.shape[0], 1))
#         return counts
# 
#     def alphabet_percycle(self, percent=False):
#         results = []
#         fa_generator = fasta_iter(self.f)
#         seqs = [fa[1] for fa in islice(fa_generator, 0, 500000)]
#         while seqs:
#             counts = izip_longest(*[[p.count(k) for k in "ATGCN"] for p in izip_longest(*seqs, fillvalue='')], fillvalue=0)
#             results.extend(counts)
#             seqs = [fa[1] for fa in islice(fa_generator, 0, 500000)]
# 
#         results2 = np.array(list(izip_longest(*results, fillvalue=0)))
#         m = results2.shape[0]
#         n = len("ATGCN")
#         counts = np.zeros((m, n), dtype=np.int)
#         for i in range(n):
#             counts[:,i] = results2[:,i::n].sum(axis=1)
# 
#         if percent:
#             counts = counts*1.0/counts.sum(axis=1).reshape((counts.shape[0], 1))
#         return counts

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    f = "./sample/s2.fa"

    t = time.time()
    for i,j in enumerate(fasta_iter(f, blocksize=int(1e7))):
        pass
    print i
    print "fasta_iter", time.time() - t
