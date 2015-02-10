#! /usr/bin/env python2
import sys

import argparse

from titlecase import titlecase

#### Handle different methods of input

parser = argparse.ArgumentParser()

# This allows us to take input from a file or from stdin (defaults to stdin)
parser.add_argument('input',
                    type=argparse.FileType('r'),
                    nargs=1,
                    help='Input stream/file')

parser.add_argument('--debug',
                    action='store_true',
                    default=False)

args = parser.parse_args()

####

with open(args.input, 'r') as infile:
    for line in infile:
        print titlecase(line)
