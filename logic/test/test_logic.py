"""A test module to see examples of import and toml in action!"""

from logic.common import math_utils  # this line serves as an example of how to import


def perform_import_example(num1):
    """Currently, this is just a placeholder to show how we can import correctly.
    
    Note how we import math_utils and then successfully use its functions
    """

    print ("-- test_logic.py : perform_import_example()")
    return math_utils.add_one(num1)
    
