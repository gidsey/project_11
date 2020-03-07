class StatusConverter:
    """
    URL Converter. Thanks to @zen on Treehouse Slack for highlighting this feature :)
    """
    regex = 'liked|disliked'

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return '%s' % value