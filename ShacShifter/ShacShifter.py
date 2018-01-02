#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')))

from ShacShifter.ExampleHTMLWriter import ExampleHTMLWriter
from ShacShifter.RDFormsWriter import RDFormsWriter
from ShacShifter.ShapeParser import ShapeParser


class ShacShifter:
    """The ShacShifter class."""

    def shift(self, input, output, format):
        """Transform input to output with format."""
        parser = ShapeParser()
        parseResult = parser.parseShape(input)
        if (format == "html"):
            writer = ExampleHTMLWriter()
        elif (format == "rdforms"):
            writer = RDFormsWriter()
        else:
            writer = None
        writer.write(parseResult, output)
