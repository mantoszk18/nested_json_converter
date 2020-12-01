"""
Set of custom exceptions for handling RecordsToTreeConverter errors.

"""

class DataAttributeMissingError(Exception): pass

class InvalidDataStructureError(Exception): pass

class DuplicateNodesFoundError(Exception): pass

class MissingNodeError(Exception): pass

class MissingRecordError(Exception): pass

class MissingNestingLevelsError(Exception): pass

class BranchDoesNotExist(Exception): pass

class NoTreeCreatedError(Exception): pass