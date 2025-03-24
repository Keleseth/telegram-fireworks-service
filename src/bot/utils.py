from telegram.helpers import escape_markdown

MARCDOWN_VERSION = 2


def croling_content(content: str) -> str:
    return escape_markdown(content, version=MARCDOWN_VERSION)
