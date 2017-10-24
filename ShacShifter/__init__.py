import argparse
from .ShacShifter import ShacShifter
from .modules.NodeShape import NodeShape
from .modules.PropertyShape import PropertyShape


def main(args=None):
    """The main method of ShacShifter."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--shacl', type=str, help="The input SHACL file")
    parser.add_argument('-o', '--output', type=str, help="The output file")
    parser.add_argument('-f', '--format', type=str, choices=[
        'rdforms',
        'wisski'
    ], help="The output format")

    args = parser.parse_args()

    shifter = ShacShifter()
    print('Das hab ich:', args.shacl, args.output, args.format)
    shifter.shift(args.shacl, args.output, args.format)
