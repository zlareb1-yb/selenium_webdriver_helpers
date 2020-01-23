# -*- coding: utf-8 -*-
'''Python module for utility functions'''

# pylint: disable=too-many-branches, too-many-statements
# pyling: disable=too-many-return-statements

import random
import os
import string
import uuid
import functools
from copy import deepcopy
import time


def manual(test):
    '''
    This decorator marks a test case as a manual test case.
    Args:
        test (object): The callable being decorated.
    Returns:
        (object): The decorated callable.
    '''

    test.manual = True
    return test


def get_unique_id(length=10):
    '''
    return unique id of specified length
    Args:
        length(int): Length of unique id
    Return:
        :str: unique id
    '''

    return str(uuid.uuid4())[-length:]


def set_spec_values_to_none(spec):
    '''
    set all values of child keys in spec to None. This is used in
    get_* methods for returning spec values
    Args:
        :spec (dict): any spec to be set to None.
    Returns:
        :dict: spec initialized to None
    '''

    temp_spec = deepcopy(spec)

    def _set_to_none(spec, subspec=None, key=None):
        if isinstance(spec, dict):
            for key, value in spec.items():
                if isinstance(value, str) or isinstance(value, bool):
                    spec[key] = None
                else:
                    _set_to_none(value, spec, key)

        elif isinstance(spec, list):
            for element in spec:
                if isinstance(element, dict):
                    _set_to_none(element)
                else:
                    subspec[key] = None
                    break


    _set_to_none(temp_spec)
    return temp_spec


def validate_kwargs(*specs):
    def valid_kwargs(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            invalid_args = []
            for key, _ in kwargs.items():
                not_found = True
                for spec in specs:
                    if key in spec:
                        not_found = False
                        break
                    else:
                        not_found = True
                if not_found:
                    invalid_args.append(key)
            if invalid_args:
                raise ValueError(
                    'list of invalid arguments to {0}: {1}'.format(
                        func.__name__, invalid_args
                    )
                )
            return func(*args, **kwargs)
        return wrapper
    return valid_kwargs


def retries(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        count = 3
        while count >= 1:
            try:
                return func(*args, **kwargs)
            except Exception:
                if count == 1:
                    raise
                time.sleep(1)
                count -= 1

    return wrapper

def format_raw_task_output(raw_output):
    """
    Formats the output given by ui.lib.application::LaunchPage::
    get_task_output_from_action() into a dictionary format.
    Args:
        raw_output (str): Multi-line str output given by above function.
    Returns:
        (dict): The dict contains keys for ['output', ..].
    """
    output_dict = {}
    raw_output_lines = raw_output.split("\n")

    try:
        output_start_index = raw_output_lines.index("1") + 1
        output_dict['output'] = [raw_output_lines[i]
                                 for i in range(output_start_index,
                                                len(raw_output_lines), 2)]
    except ValueError:
        output_dict['output'] = []

    # TODO - Populate dictionary with other useful info like status,
    # TODO - start and end time.

    return output_dict

def get_random_int(min=0, max=9999999):
  """
  Generates a random integer between min and max.
  Args:
    min (int): Lower bound.
    max (int): Upper bound.
  Returns:
    (str): Stringified random integer.
  """
  return str(random.randint(min, max))

def get_random_string(length=10):
  """
  Generates a random string of length 'length'.
  Args:
    length (str): Length of the string.
  Returns:
    (str): A random string
  """
  return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase +
                               string.digits) for _ in range(length))

def get_random_date():
  """
  Generates a random date.
  Returns:
    (str): A random date in the DD/MM/YYYY format.
  """
  return "%.2d/%.2d/%.4d" %(random.randrange(1, 28),
                            random.randrange(1, 12),
                            random.randrange(1970, 2040))

def get_random_time():
  """
  Generates a random time in the 24 hour format.
  Returns:
    (str): A random time.
  """
  return "%.2d:%.2d:%.2d" %(random.randrange(1, 24),
                            random.randrange(1, 60),
                            random.randrange(1, 60))

def get_random_date_time():
  """
  Generates a random date time string.
  Returns:
    (str): A random date time string in the DD/MM/YYYY - HH:MM:SS format.
  """
  return "%s T%s" % (get_random_date(), get_random_time())

def get_random_multiline_string():
  """
  Generates a random multiline string of variable line length.
  Returns:
    (str): A random multiline string.
  """
  lines_count = random.randint(2, 5)
  lines = [get_random_string() for _ in range(lines_count)]
  return "\n".join(lines)


def get_diff_between_lists_of_dicts(list1, list2):
    """
    This routine returns difference between two lists of dictionaries
    Args:
        list1(List): list from which difference needs to be calculated
        list2(List): list whose items will be removed from list1
    Returns:
        (List): Difference between two lists (list1-list2)
    """

    list2_dicts_with_count = {}
    difference = []

    for item in list2:
        item = frozenset(item.items())
        list2_dicts_with_count[item] = list2_dicts_with_count.get(item, 0) + 1

    for item in list1:
        key = frozenset(item.items())

        if not list2_dicts_with_count.get(key, 0):
            difference.append(item)
        else:
            list2_dicts_with_count[key] -= 1

    return difference

def get_script_folder_path():
    """
    This routine returns the script folder path

    Returns:
         str: script folder path
    """
    current_path = os.path.dirname(os.path.realpath(__file__))
    script_folder = "{}/script".format(current_path)
    return script_folder

def set_locator(locator, placeholder):
    '''
    This routine generates the locator based on index or string; useful in case of adding list of items
    Args:
        locator(tuple): locator value
        placeholder(String/Integer): To modify locator based on index/string
    Returns
        tuple: customized locator based on index or string
    '''

    specific_locator = list(locator)
    specific_locator[1] %= placeholder
    return tuple(specific_locator)