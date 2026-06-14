import bleach

ALLOWED_TAGS = [
    'p', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'strong', 'em', 'b', 'i',
    'code', 'pre', 'blockquote', 'a', 'hr',
]
ALLOWED_ATTRS = {
    'a': ['href', 'title'],
}


def sanitize(text):
    return bleach.clean(text or '', tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)
