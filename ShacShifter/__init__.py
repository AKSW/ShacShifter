import argparse
import logging
from .ShacShifter import ShacShifter


def main(args=None):
    """The main method of ShacShifter."""
    werkzeugLogger = logging.getLogger('werkzeug')
    werkzeugLogger.setLevel(logging.INFO)

    logger = logging.getLogger('ShacShifter')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # create console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--shacl', type=str, help="The input SHACL file")
    parser.add_argument('-o', '--output', type=str, help="The output file")
    parser.add_argument('-f', '--format', type=str, choices=[
        'rdforms',
        'wisski',
        'html'
    ], help="The output format")
    parser.add_argument('-l', '--logfile', type=str, help="The log file")
    parser.add_argument('-v', '--verbose', action="store_true")
    parser.add_argument('-vv', '--verboseverbose', action="store_true")
    parser.add_argument('-se', '--sparqlEndpoint', type=str, help="The Sparql Endpoint")
    parser.add_argument('-ri', '--resourceIRI', type=str, help="The resource IRI")
    parser.add_argument('-ng', '--namedGraph', type=str, help="The named Graph")

    args = parser.parse_args()

    ch.setLevel(logging.ERROR)

    if args.verbose:
        ch.setLevel(logging.INFO)

    if args.verboseverbose:
        ch.setLevel(logging.DEBUG)

    logger.addHandler(ch)

    if args.logfile:
        try:
            fh = logging.FileHandler(args.logfile)
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        except Exception:
            logger.info('Could not initialize FileHandler for logging.')
    logger.debug('Logger initialized')

    shifter = ShacShifter()
    shifter.shift(args.shacl, args.output, args.format, args.sparqlEndpoint,
                  args.resourceIRI, args.namedGraph)
