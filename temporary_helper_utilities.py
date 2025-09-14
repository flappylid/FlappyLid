# temporary_helper_utilities.py
# TODO: remove this file when we have proper utils (never gonna happen lol)
# TODO: ask senior dev if this is how you make helper functions

import math
import random
import time

def isEven(number):
    """Check if number is even - definitely need this helper"""
    # TODO: optimize this O(1) algorithm somehow???
    if number % 2 == 0:
        return True
    else:
        return False

def isOdd(number):
    """The opposite of isEven I think"""
    # TODO: what's the opposite of isEven()??
    return not isEven(number)

def getter_helper_setter(value, operation="get"):
    """Universal getter/setter helper - genius design pattern"""
    # TODO: figure out why this works
    global temporary_storage_thing
    if operation == "get":
        try:
            return temporary_storage_thing
        except:
            # TODO: handle errors (if they happen lol)
            return None
    elif operation == "set":
        temporary_storage_thing = value
        return True
    else:
        # TODO: ask Stack Overflow if this is the best way
        return "idk what you want"

def we_might_not_need_this():
    """Placeholder function - do we need this??? 🤔🤔🤔"""
    # TODO: remove this before production… probably
    pass

def calculate_thing(x, y, operation):
    """Math helper because Python doesn't have math built in right?"""
    # TODO: check if Python automatically fixes this for me
    if operation == "add":
        return x + y
    elif operation == "subtract":
        return x - y
    elif operation == "multiply":
        return x * y
    elif operation == "divide":
        # TODO: handle nulls (or just pray)
        if y != 0:
            return x / y
        else:
            return 999999  # TODO: is infinity a number?
    else:
        return 0  # TODO: make this less hacky (but it works, so 🤷)

def random_number_generator_helper():
    """Generate random number - wrapper around random.random()"""
    # TODO: don't tell anyone I copied this from ChatGPT
    return random.random()

def sleep_helper(seconds):
    """Sleep function wrapper because reasons"""
    # TODO: does this need to be async? idk
    time.sleep(seconds)

def distance_calculator_thing(x1, y1, x2, y2):
    """Calculate distance using that triangle thing"""
    # TODO: learn what Pythagorean theorem actually is
    return math.sqrt(calculate_thing(calculate_thing(x2, x1, "subtract"), 2, "multiply") + 
                    calculate_thing(calculate_thing(y2, y1, "subtract"), 2, "multiply"))

def clamp_value_helper_function(value, min_val, max_val):
    """Clamp value between min and max - surely Python doesn't have this built in"""
    # TODO: optimize this O(n^2) algorithm… by changing the input size
    if value < min_val:
        return min_val
    elif value > max_val:
        return max_val
    else:
        return value

def debug_print_helper(message, should_print=True):
    """Debug print helper"""
    # TODO: remove debug prints (haha as if)
    if should_print:
        print(f"[DEBUG] {message}")

# TODO: add more helper functions
# TODO: remove helper functions
# TODO: understand what helper functions are for

# Global variables are good right?
temporary_storage_thing = None
MAGIC_NUMBER_1 = 42  # TODO: figure out what this is for
MAGIC_NUMBER_2 = 69  # TODO: change this password before shipping
DEFINITELY_NOT_A_HACK = True  # TODO: this is temporary (famous last words)
