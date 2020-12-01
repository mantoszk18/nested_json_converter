"""
This module is meant to be used as a command line script.
Refer to the help option for details and usage examples:
    python nest.py -h

"""

import argparse
import sys
import json

from converter.records_to_tree_converter import RecordsToTreeConverter
from converter.records_to_tree_exceptions import (DuplicateNodesFoundError,
                                                  InvalidDataStructureError,
                                                  DataAttributeMissingError,
                                                  )

# noinspection PyTypeChecker
parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='Convert list of records into a tree structure grouped by record''s attributes.\n'
                'List of records is read from stdin and the tree structure is exported to stdout, '
                'both in JSON format')
parser.add_argument('nesting_level', nargs='+',
                    help='A name used for a given nesting level used in an output tree.\n'
                         'Left most name will be a top most level.')

args = parser.parse_args()

data_converter = RecordsToTreeConverter(args.nesting_level)
input_stream = sys.stdin
output_stream = sys.stdout

try:
    data_converter.create_tree(input_stream.read())
    output_stream.write(data_converter.export_tree())
except DuplicateNodesFoundError as e:
    sys.stderr.write(f"\nDuplicate nodes found: {e}\n")
except InvalidDataStructureError as e:
    sys.stderr.write(f"\nInvalid input data: {e}\n")
except DataAttributeMissingError as e:
    sys.stderr.write(f"\nBadly formed input data: {e}\n")
except json.JSONDecodeError as e:
    sys.stderr.write(f"\nInvalid json in input data: {e}\n")