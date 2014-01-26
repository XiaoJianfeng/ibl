#!/usr/bin/env python

import sys
import argparse
import csv
import xlsxwriter

''' convert txt file[s] to .xlsx file
usage: $0 [txt1 txt2 txt...] xlsx_file
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

def txt2xlsx(f_out, *f_in, **kwds):
    sep = kwds['sep'] if ('sep' in kwds) else '\t'

    workbook = xlsxwriter.Workbook(f_out)
    for n, fn in enumerate(f_in):
        fobj_in = sys.stdin if fn == '-' else open(fn, 'r')
        f = csv.reader(fobj_in, delimiter=sep)
        short_fn = "Sheet {}".format(n+1)
        worksheet = workbook.add_worksheet(short_fn)
        for i, row in enumerate(f):
            worksheet.write_row(i, 0, map(correct_data_type, row))
        sys.stderr.write("{num} lines in total for {name}\n".format(num=i+1, name=fn))

    workbook.close()

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='convert txt to excel xlsx')
    parser.add_argument('-d', '--delimiter', default='\t', help="delimiter for the txt file")
    parser.add_argument('input', nargs='*', default=['-'], help="input file[s], blank for stdin")
    parser.add_argument('output', help="output file")

    args = parser.parse_args()

    txt2xlsx(args.output, *args.input, sep=args.delimiter)

