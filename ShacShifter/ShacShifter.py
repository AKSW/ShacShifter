#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')))

import argparse
from ShapeParser import ShapeParser
# from RDFormsWriter import RDFormsWriter


class ShacShifter:
    def shift (self, input, output, format):
        parser = ShapeParser(input)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--shacl', type=str, help="The input SHACL file")
    parser.add_argument('-o', '--output', type=str, help="The output file")
    parser.add_argument('-f', '--format', type=str, choices=[
        'rdforms',
        'wisski'
    ], help="The output format")
    args = parser.parse_args()

    shifter = ShacShifter()
    shifter.shift(args.shacl, args.output, args.format)
