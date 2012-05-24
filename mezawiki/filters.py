from markdown import markdown


def plain(content):
    """
    Renders content using markdown (no extensions).
    """
    return markdown(content)

