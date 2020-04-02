#  Set the age ranges
AGE_RANGES = {
    'b': set(range(0, 11)),
    'y': set(range(11, 21)),
    'a': set(range(21, 90)),
    's': set(range(90, 201)),
}


def get_age_range(age_list):
    """
    Using the AGE RANGES above return the age values to search for.
    Thanks to @zen on Treehouse Slack for help and input on this.
    :param age_list:
    :return: a set of integers that includes all age values to search against
    """
    ages_set = set(age_list)
    result = set()

    if 'b' in ages_set:
        result = result | AGE_RANGES.get('b', set())
    if 'y' in ages_set:
        result = result | AGE_RANGES.get('y', set())
    if 'a' in ages_set:
        result = result | AGE_RANGES.get('a', set())
    if 's' in ages_set:
        result = result | AGE_RANGES.get('s', set())
    return result


def get_microchipped(value):
    """
    Convert store microchipped preference into boolean or 'no-preference'
    :param value: y,n,e
    :return: True, False or 'no_preference'
    """
    if value == 'n':
        return False
    if value == 'y':
        return True
    return 'no_preference'


def clean_input(value):
    """
    Remove whitespace and duplicates from user input,
    output a list of values for validation.
    :param value:
    :return: value (comma-separated string with duplicates removed)
    :return: value_list (a list of values for validation)
    """
    value = value.replace(" ", "")  # remove any whitespace
    value_list = value.split(',')  # convert to list for validation
    value_list = set(value_list)  # remove any duplicates
    value = ','.join(str(s) for s in value_list)  # convert to comma-separated string without duplicates
    return value, value_list
