import unittest
import json
import io

from anytree import RenderTree

from converter.records_to_tree_converter import RecordsToTreeConverter
from converter.records_to_tree_exceptions import *


class RecordsToTreeConverterTestCase(unittest.TestCase):

    def setUp(self):
        self.converter = RecordsToTreeConverter(['currency', 'country', 'city'])


class ConvertInputDataTestCase(RecordsToTreeConverterTestCase):

    def test_validate_input_data_success(self):
        with open('correct_input_data.json') as correct_data:
            correct_input_data = json.loads(correct_data.read())
            self.assertTrue(self.converter._validate_input_data(correct_input_data))

    def test_validate_input_data_nesting_level_attribute_missing_raises_exception(self):
        with open('attribute_missing_input_data.json') as missing_data:
            attribute_missing_input_data = json.loads(missing_data.read())
            self.assertRaises(DataAttributeMissingError, self.converter._validate_input_data, attribute_missing_input_data)

    def test_validate_input_data_empty_data_raises_exception(self):
        empty_data = []
        self.assertRaises(InvalidDataStructureError, self.converter._validate_input_data, empty_data)

    def test_validate_input_data_not_a_list_of_dicts_raises_exception(self):
        invalid_structure = '{"strange_key": ["strange", "list"]}'
        another_invalid_structure = '["what", "is", "this?"]'
        self.assertRaises(InvalidDataStructureError, self.converter._validate_input_data, invalid_structure)
        self.assertRaises(InvalidDataStructureError, self.converter._validate_input_data, another_invalid_structure)


class BuildBranchTestCase(RecordsToTreeConverterTestCase):

    def test_build_branch_success(self):
        with open('branch_correct_input_data.json') as correct_data:
            correct_input_data = json.loads(correct_data.read())

        # we're building a single currency (top nesting level) branches
        first_record, second_record, third_record = correct_input_data
        leaf_node = self.converter._build_branch(self.converter.nesting_levels[:],
                                                 self.converter.root_node,
                                                 first_record)
        self.assertEqual("Node('/root/EUR/FR/Paris')", str(leaf_node))

        leaf_node = self.converter._build_branch(self.converter.nesting_levels[:],
                                                 self.converter.root_node,
                                                 second_record)
        self.assertEqual("Node('/root/EUR/FR/Lyon')", str(leaf_node))

        leaf_node = self.converter._build_branch(self.converter.nesting_levels[:],
                                                 self.converter.root_node,
                                                 third_record)
        self.assertEqual("Node('/root/EUR/ES/Madrid')", str(leaf_node))

    def test_build_branch_nesting_levels_empty_or_None_raises_exception(self):
        with open('branch_correct_input_data.json') as correct_data:
            correct_input_data = json.loads(correct_data.read())

        first_record = correct_input_data[0]
        self.assertRaises(MissingNestingLevelsError,
                          self.converter._build_branch,
                          [], self.converter.root_node, first_record)
        self.assertRaises(MissingNestingLevelsError,
                          self.converter._build_branch,
                          None, self.converter.root_node, first_record)

    def test_build_branch_no_node_raises_exception(self):
        with open('branch_correct_input_data.json') as correct_data:
            correct_input_data = json.loads(correct_data.read())

        first_record = correct_input_data[0]
        self.assertRaises(MissingNodeError,
                          self.converter._build_branch,
                          self.converter.nesting_levels[:], None, first_record)

    def test_build_branch_record_empty_or_None_raises_exception(self):
        self.assertRaises(MissingRecordError,
                          self.converter._build_branch,
                          self.converter.nesting_levels[:], self.converter.root_node, {})
        self.assertRaises(MissingRecordError,
                          self.converter._build_branch,
                          self.converter.nesting_levels[:], self.converter.root_node, None)

    def test_build_branch_duplicate_nodes_raises_exception(self):
        with open('branch_with_duplicates_input_data.json') as correct_data:
            correct_input_data = json.loads(correct_data.read())

        first_record, duplicate_record = correct_input_data
        self.converter._build_branch(self.converter.nesting_levels[:],
                                     self.converter.root_node,
                                     first_record)

        self.assertRaises(DuplicateNodesFoundError,
                          self.converter._build_branch,
                          self.converter.nesting_levels[:], self.converter.root_node, first_record)



class CreateTreeTestCase(RecordsToTreeConverterTestCase):

    def test_create_tree_success(self):
        with open('correct_tree_structure.txt') as correct_tree:
            expected_tree = correct_tree.read()
        with open('correct_input_data.json') as correct_data:
            self.converter.create_tree(correct_data.read())
            actual_tree = str(RenderTree(self.converter.root_node))
            actual_tree += '\n'  # due to file.read() adding a new line at the end
            self.assertEqual(expected_tree, actual_tree)

    def test_create_tree_invalid_json_raises_exception(self):
        self.assertRaises(json.JSONDecodeError, self.converter.create_tree, "")


class ExportTreeTestCase(RecordsToTreeConverterTestCase):

    def test_export_tree_success(self):
        with open('correct_input_data.json') as correct_data:
            self.converter.create_tree(correct_data.read())
        with open('correct_output_data.json') as correct_output_data:
            correct_output = correct_output_data.read()

        actual_output = self.converter.export_tree()
        actual_output += '\n'  # due to file.read() adding a new line at the end
        self.assertEqual(correct_output, actual_output)

    def test_export_tree_no_tree_created_raises_exception(self):
        self.assertRaises(NoTreeCreatedError, self.converter.export_tree)


if __name__ == '__main__':
    unittest.main()
