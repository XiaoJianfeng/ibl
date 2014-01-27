#!/usr/bin/env python

import sys
import argparse
import csv
import re
from operator import itemgetter
from compiler.ast import flatten

"""
like cut, but the order of fields are preserved.

usage: cut2 [-h] [-d DELIMITER] [-o OUTPUT] [-f FIELDS] [input]

work likes cut, but the order of columns are reserved, and duplicate columns
are also reserved.

positional arguments:
  input                 input file, blank for stdin

optional arguments:
  -h, --help            show this help message and exit
  -d DELIMITER, --delimiter DELIMITER
                        delimiter for the txt file
  -o OUTPUT, --output OUTPUT
                        output file, default to stdout
  -f FIELDS, --fields FIELDS
                        fields to cut, the number starts from 1. For example,
                        '2', '3,2,5-8', '3-', ' -3,5,2'(note the preceding
                        blank here)

Note:
1) column numbers starts from 1, not 0 as in python.

2) what flatten does:
   >>> flatten([0, [1, 2], [3, 4, [5, 6]], 7])
   [0, 1, 2, 3, 4, 5, 6, 7]
   >>> flatten(['a', ['b','c']])
   ['a', 'b', 'c']
   >>> flatten(['aaa', 'bbb'])
   ['aaa', 'bbb']
"""

#-----------------------------------------------------------------------------
def fieldgetter(fields):
    """ parse fields which is a string.
    exmaples of valide fields:
        1
        5,2,1
        2,3-4,6-
    """

    # remove ' '
    fields = fields.strip().replace(' ', '')  

    idx = []  # the return value
    items = fields.split(',')
    for item in items:
        if item.isdigit():
            start = int(item) - 1
            if start >= 0:
                idx.append(start)
            else:
                raise Exception("invlid fields: {} in {}".format(item, fields))
        elif item.count('-') == 1:
            start, _, stop = item.partition('-')
            if start == '' and stop == '':
                raise Exception("invlid fields: {} in {}".format(item, fields))
            start = 0 if start == '' else int(start) - 1
            stop = None if stop == '' else int(stop)
            idx.append(slice(start, stop))
        else:
            raise Exception("invlid fields: {} in {}".format(item, fields))

    def func(row):
        result = []
        L = len(row)
        for i in idx:
            if isinstance(i, int) and 0 <= i < L:
                result.append(row[i])
            elif isinstance(i, slice):
                result.extend(row[i])
        return result
    return func

def cut2(f_in, fields, f_out='-', delimiter='\t'):
    """
    Cut fields specified by fields.

    Both f_in and f_out could be a string, which is treated as file name, or a file object.
    """

    if isinstance(f_out, basestring):
        fobj_out = sys.stdout if (f_out == '-') else open(f_out, 'w')
    elif isinstance(f_out, file):
        fobj_out = f_out
    else:
        raise Exception("Invalid file: %s" % f_out)

    if isinstance(f_in, basestring):
        fobj_in = sys.stdin if (f_in == '-') else open(f_in, 'r')
    elif isinstance(f_in, file):
        fobj_in = f_in
    else:
        raise Exception("Invalid file: %s" % f_in)

    if fields is None:
        raise Exception("You must specify the fields you want to cut.")

    get_field = fieldgetter(fields)

    f = csv.reader(fobj_in, delimiter=delimiter)

    fobj_out.writelines(("%s\n" % delimiter.join(get_field(row))) for row in f)
    #for row in f:
    #    line = get_field(row)
    #    fobj_out.write("%s\n" % delimiter.join(line))
        

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='work likes cut, but the order of columns are reserved, \
            and duplicate columns are also reserved.')
    parser.add_argument('-d', '--delimiter', default='\t', help="delimiter for the txt file")
    parser.add_argument('-o', '--output', default='-', help="output file, default to stdout")
    parser.add_argument('-f', '--fields', help="fields to cut, the number starts from 1. \
            For example, '2', '3,2,5-8', '3-', ' -3,5,2'(note the preceding blank here) ")
    parser.add_argument('input', nargs='?', default='-', help="input file, blank for stdin")

    args = parser.parse_args()

    try:
        cut2(f_in=args.input, fields=args.fields, f_out=args.output, delimiter=args.delimiter)
    except Exception as e:
        sys.stderr.write("cut2: {}\nTry `cut2 --help' for more information.".format(e))
        sys.exit()
