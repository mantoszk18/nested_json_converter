"""
This module allows converting JSON lists of records to a tree structure.

"""

import sys
import json

from typing import TextIO
from anytree import Node

from converter.records_to_tree_exceptions import (InvalidDataStructureError,
                                                 DataAttributeMissingError,
                                                 DuplicateNodesFoundError,
                                                 MissingNodeError,
                                                 MissingNestingLevelsError,
                                                 MissingRecordError,
                                                 NoTreeCreatedError,
                                                )


class RecordsToTreeConverter:
    """
    Allows converting JSON lists of records into a tree structure.
    By default uses stdin and stdout as input and output streams.

    """
    EXPORT_JSON_INDENT = 2

    def __init__(self, nesting_levels: list):
        self.nesting_levels = nesting_levels
        self.root_node = Node('root')

    def _validate_input_data(self, input_data: list) -> bool:
        """
        Converts input data from JSON and validates if a tree can be created..

        Args:
            input_data: JSON string containing data to be converted

        Returns:
            boolean: True if validation was successful

        """
        is_input_data_valid = True
        is_input_data_a_list = isinstance(input_data, list)
        input_data_contains_only_dicts = True

        if is_input_data_a_list:
            input_data_contains_only_dicts = all({isinstance(record, dict) for record in input_data})
        if not (input_data and is_input_data_a_list and input_data_contains_only_dicts):
            raise InvalidDataStructureError("Input data should be a non-empty list of dictionaries.")

        missing_count = 0
        for record in input_data:
            missing_elements = set(self.nesting_levels) - record.keys()
            if missing_elements:
                missing_count += 1
                sys.stderr.write(f"Elements missing for record {record.values()}\n")
        if missing_count:
            raise DataAttributeMissingError(f"Key elements were missing in {missing_count} records")

        return is_input_data_valid

    def create_tree(self, input_data: str):
        """
        Creates a tree from an input stream data.
        Children nodes are unsorted at this stage - sorting happens during export.
        Does the validation of the input data as well.
        If build_branch throws an error, the whole tree needs to be recreated using corrected data.

        """
        loaded_data = json.loads(input_data)

        if self._validate_input_data(loaded_data):
            for record in loaded_data:
                leaf_node = self._build_branch(self.nesting_levels[:], self.root_node, record)
                remaining_keys = record.keys() ^ set(self.nesting_levels)
                leaf_node.values = [{k: record[k] for k in remaining_keys}]

    def _build_branch(self, remaining_nesting_levels: list, current_node: Node, record: dict) -> Node:
        """
        This method builds branches recursively. Duplicate nodes are signalled through exception.

        Args:
            remaining_inverted_nesting_levels: Levels to still add to the tree.
            next_node: Next node to be added
            record: Currently processed data record

        Returns:
            Node: Leaf node of the given branch

        """
        if current_node is None:
            raise MissingNodeError
        if record is None or not record:
            raise MissingRecordError

        if remaining_nesting_levels:
            next_level = record[remaining_nesting_levels.pop(0)]
            existing_nodes = [node for node in current_node.children if node.name == next_level]

            if len(existing_nodes) > 1:
                raise DuplicateNodesFoundError(f"Duplicate found in the children of {record.values()}")
            if existing_nodes and not remaining_nesting_levels:
                raise DuplicateNodesFoundError(f"Duplicate found at {record.values()}")

            next_node = existing_nodes or [Node(next_level, parent=current_node)]
            current_node = self._build_branch(remaining_nesting_levels, next_node[0], record)
        elif remaining_nesting_levels is None or (not remaining_nesting_levels and current_node == self.root_node):
            raise MissingNestingLevelsError("Cannot build tree branch without nesting levels.")

        return current_node

    def export_tree(self) -> str:
        """
        Exports the tree to the output stream

        Args:
            output_stream: A textIO stream of your choice (stdout by default)

        """
        if not self.root_node.children:
            raise NoTreeCreatedError("No tree to export. Run create_tree method first.")

        output_dict = {}
        self._export_layer(self.root_node, output_dict)

        output_json = json.dumps(output_dict, sort_keys=True, indent=self.EXPORT_JSON_INDENT)

        return output_json

    def _export_layer(self, current_node: Node, current_dict: dict ) -> list:
        """
        Exporting process helper method to process the tree recursively.

        Args:
            current_node: Node whose children will be converted to dictionary keys
            current_dict: Dictionary object to be filled in with nested keys.
                          This is a referenced object, so should be updated - not replaced

        Returns:
            list: If current_node is a leaf node, return list of a dictionary of remaining keys and values.

        """
        if current_node.is_leaf:
            return current_node.values

        layer_keys = [node.name for node in current_node.children]
        current_dict.update({ key: {} for key in layer_keys})

        for child_node in current_node.children:
            values = self._export_layer(child_node, current_dict[child_node.name])
            if values:
                current_dict[child_node.name] = values