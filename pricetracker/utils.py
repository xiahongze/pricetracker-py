import re

spaces = re.compile(r'\s*')


def clean_text(text: str):
    return spaces.sub('', text)
