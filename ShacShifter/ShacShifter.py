#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')))

from ShacShifter.HTMLSerializer import HTMLSerializer
from ShacShifter.RDFormsWriter import RDFormsWriter
from ShacShifter.ShapeParser import ShapeParser
import logging


class ShacShifter:
    """The ShacShifter class."""

    logger = logging.getLogger('ShacShifter')

    # def __init__(self):
    def shift(self, input, output, format):
        """Transform input to output with format."""
        self.logger.debug('Start Shifting from {} into {}'.format(input, output))
        parser = ShapeParser()
        parseResult = parser.parseShape(input)
        if (format == "html"):
            writer = HTMLSerializer(parseResult, output)
        elif (format == "rdforms"):
            writer = RDFormsWriter()
        else:
            writer = None
        # writer.write(parseResult, output)
