import sys

text_type = str
if sys.version_info < (3,):
    text_type = unicode # noqa
