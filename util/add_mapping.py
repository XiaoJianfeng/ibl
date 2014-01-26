#!/usr/bin/env python

# function: add mapping of first column to second column
# usage: $0 mapping_file input_file > output_file
#         input_file could be missing, then stdin will be used
#
# last modified:
#    2014.01.26 - add argparse to process arguments
#                 and restructure the program
#    2013.10.08 - will print error message when raise exception
#    2012.06.27


import sys
import csv

#-------------------------------------------------------------------
# so python will exit gracefully when in a pipe
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL) 

#-------------------------------------------------------------------

def add_mapping(source, mapping, output='-', field_a=0, field_b=0, delimiter='\t', NA=None):
    """
    add mapping info from 'mapping' to 'source', write to 'output'

usage: add_mapping2.py [-h] [-d DELIMITER] [-o OUTPUT] [-a A] [-b B] [-N NA]
                       mapping [source]

add mapping info to input file. mapping_file input_file > output_file

positional arguments:
  mapping               mapping file, which should have two columns, the first
                        column is id, the second colum is info that will be
                        added to output.
  source                input file, blank or '-' for stdin

optional arguments:
  -h, --help            show this help message and exit
  -d DELIMITER, --delimiter DELIMITER
                        delimiter for the input file, default to '\t'
  -o OUTPUT, --output OUTPUT
                        output file, default to stdout
  -a A                  field in source file to be matched
  -b B                  field in output file for matched mapping
  -N NA, --NA NA        replacement when the mapping is not available for an
                        item. NA is one of (None, 'NA', 'other_string').
    """

    if isinstance(source, basestring):
        f_in = sys.stdin if source == '-' else open(source, 'r')
    elif isinstance(source, file):
        f_in = source
    else:
        raise Exception("source file {} should be a file path or file obj".format(source))

    if output == '-':
        f_out = sys.stdout
    else:
        f_out = open(output, 'w')


    # mapping_file should have two items in one line. 
    id_info = dict(ln.rstrip("\n").split("\t") for ln in open(mapping) if '\t' in ln)  # partition()?

    for ln in csv.reader(f_in, delimiter=delimiter):
        name = ln[field_a]
        name = name.strip('"\'\n') # the ENSG name in input file may be surrounded by '"', and if there is only one column, name will end with "\n"
        try:
            ln[field_b:field_b] = [id_info.get(name, (NA or name))]
        except Exception, e:
            sys.stderr.write(str(e))
            raise
        f_out.write("%s\n" % delimiter.join(ln))

#-------------------------------------------------------------------
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='add mapping info to input file.\n mapping_file input_file > output_file')
    parser.add_argument('-d', '--delimiter', default='\t', help="delimiter for the input file, default to '\\t'")
    parser.add_argument('-o', '--output', default='-', help="output file, default to stdout")
    parser.add_argument('-a', default=0, type=int, help="field in source file to be matched")
    parser.add_argument('-b', default=1, type=int, help="field in output file for matched mapping")
    parser.add_argument('-N', '--NA', default=None, help="replacement when the mapping is not available for an item. NA is one of (None, 'NA', 'other_string'). ")
    parser.add_argument('mapping', help="mapping file, which should have two columns, the first column is id, the second colum is info that will be added to output.")
    parser.add_argument('source', nargs='?', default='-', help="input file, blank or '-' for stdin")

    args = parser.parse_args()

    add_mapping(source=args.source, mapping=args.mapping, output=args.output, field_a=args.a, field_b=args.b, delimiter=args.delimiter, NA=args.NA)
