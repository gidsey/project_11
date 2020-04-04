# noinspection PyMethodMayBeStatic
class StatusConverter:
    """
    URL Converter. Thanks to @zen on Treehouse Slack for highlighting this feature :)
    """
    regex = 'liked|disliked|undecided'

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return '%s' % value


# noinspection PyMethodMayBeStatic
class BlacklistConverter:

    regex = 'true|false'

    def to_python(self, value):
        return str(value).title()

    def to_url(self, value):
        return '%s' % value
