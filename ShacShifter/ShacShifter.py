#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')))

import argparse
from ShacShifter import ShapeParser
# from RDFormsWriter import RDFormsWriter


class ShacShifter:
    """The ShacShifter class."""

    def shift(self, input, output, format):
        """Transform input to output with format."""
        parser = ShapeParser(input)
