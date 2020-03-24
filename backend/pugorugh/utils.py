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
























# def get_age_range(age_list):
#     """Determines the lowest and highest age range
#     values based off a list of characters.
#
#     Args:
#         age_list (List): A list of characters representing
#          age ranges such as: ['b', 'y', 'a', 's']
#
#     Returns:
#         A dictionary containing age range search parameters
#          for each age category.
#
#     """
#     ages = set(age_list)
#
#     age_ranges = {
#         'baby_start': -1, 'baby_end': -1,
#         'young_start': -1, 'young_end': -1,
#         'adult_start': -1, 'adult_end': -1,
#         'senior_start': -1, 'senior_end': -1,
#     }
#
#     # Set the age ranges
#     if 'b' in ages:
#         age_ranges.update({'baby_start': 0, 'baby_end': 10})
#     if 'y' in ages:
#         age_ranges.update({'young_start': 11, 'young_end': 20})
#     if 'a' in ages:
#         age_ranges.update({'adult_start': 21, 'adult_end': 89})
#     if 's' in ages:
#         age_ranges.update({'senior_start': 90, 'senior_end': 200})
#
#     return age_ranges


