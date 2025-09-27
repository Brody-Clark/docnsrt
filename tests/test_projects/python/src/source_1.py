# Test file for parsing and documentation generation

database = Database()


class InvalidUserException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


# This function should be skipped since it is commented out
# def func_1():
#     print("helo")


def string_manip(s):
    s = s[::-1]
    return s


def login(user, p):
    """ Logs a user in. """
    if len(user) == 0 or len(p) == 0:
        raise ValueError("field cannot be empty")
    try:
        database.login(user, p)
    except Exception as e:
        print(e)
        raise InvalidUserException(f"{user} not found")


class Math:

    def calculate_area(self, length, width):
        """Calculates the area of a rectangle.

        Args:
            length (int): The length of the rectangle.
            width (int): The width of the rectangle.

        Returns:
            int: The area of the rectangle.
        """
        return length * width

    def calc(self, perimeter: int, num: int, other_num: float):
        if other_num < 0:
            raise ValueError("other_num must be positive")
        perimeter = num + 1 + other_num
        return perimeter
