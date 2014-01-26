#!/usr/bin/env python

import sys
import argparse
import csv
from types import StringTypes
#import xlsxwriter
import xlwt


''' convert txt file[s] to .xls file
usage: $0 [txt1 txt2 txt...] xls_file
multiple txts will be added as separate excel sheet
'''

#-----------------------------------------------------------------------------
def correct_data_type(v):
    """ convert v to int if possible, else float if possible, else just return as it is"""
    try:
        return int(v)
    except:
        try:
            return float(v)
        except:
            return v

def txt2xls(f_out, *f_in, **kwds):
    sep = kwds['sep'] if ('sep' in kwds) else '\t'

    workbook = xlwt.Workbook()
    for n, fn in enumerate(f_in):
        fobj_in = sys.stdin if fn == '-' else open(fn, 'r')
        f = csv.reader(fobj_in, delimiter=sep)
        short_fn = "Sheet {}".format(n+1)
        worksheet = workbook.add_sheet(short_fn)
        for i, row in enumerate(f):
            for j, item in enumerate(map(correct_data_type, row)):
                if item and isinstance(item, StringTypes) and item[0] == '=': # a formula
                    worksheet.write(i, j, xlwt.Formula(item[1:]))
                else:              # not a formula
                    worksheet.write(i, j, item)
        sys.stderr.write("{num} lines in total for {name}\n".format(num=i+1, name=fn))

    workbook.save(f_out)

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='convert txt to excel xls')
    parser.add_argument('-d', '--delimiter', default='\t', help="delimiter for the txt file")
    parser.add_argument('input', nargs='*', default=['-'], help="input file[s], blank for stdin")
    parser.add_argument('output', help="output file")

    args = parser.parse_args()

    txt2xls(args.output, *args.input, sep=args.delimiter)

