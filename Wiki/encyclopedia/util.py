import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content, update=False):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        if update:
            default_storage.delete(filename)
        else:
            return 3
    default_storage.save(filename, ContentFile(content))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8").replace("\r\n", "\n")
    except FileNotFoundError:
        return None


def md_to_html(content):
    # heading
    pattern = re.compile(r'^ {0,3}(?P<h1>#(?P<h2>#(?P<h3>#(?P<h4>#(?P<h5>#(?P<h6>#?)?)?)?)?)?) (?P<content>.+)$',
                         re.MULTILINE)
    content = pattern.sub(heading_tag, content)

    # bolding
    pattern = re.compile(r'(?P<left_side>.*?)(\*{2})(?P<content>.*?\S.*?\n?.*?)(\*{2})(?P<right_side>.*?)',
                         re.MULTILINE)
    content = pattern.sub(bold_tag, content)

    # unordered list
    pattern = re.compile(r'^ {0,3}\* +(.*?)(?!\n {0,5}#{1,6} )(?=\n\n|\Z)', re.DOTALL | re.MULTILINE)
    content = pattern.sub(ul_tag, content)

    # paragraph
    pattern = re.compile(r'\n\n?(?!<h1>|<h2>|<h3>|<h4>|<h5>|<h6>|<ul>|<li>)(?P<content>.+?)(?=\n\n|\Z)', re.MULTILINE | re.DOTALL)
    content = pattern.sub(p_tag, content).replace("\n", "")

    # links
    pattern = re.compile(r'\[(?P<content>.*?)]\((?P<link>.*?)\)')
    content = pattern.sub(a_tag, content)

    return content


def heading_tag(match):
    h = [key for key, value in match.groupdict().items() if value == '#']
    h = h[0]

    return f"<{h}>" + match.groupdict()["content"] + f"</{h}>"


def bold_tag(match):
    return match.groupdict()["left_side"] + "<strong>" + match.groupdict()["content"] + "</strong>" + match.groupdict()["right_side"]


def ul_tag(match):
    content = match.group()
    pattern = re.compile(r"^ {0,3}\* +(?P<content>.*?)(?=\n {0,3}\*|\Z)", re.DOTALL | re.MULTILINE)
    content = pattern.sub(r"<li>\g<content></li>", content)
    return r"<ul>" + content + r"</ul>"


def p_tag(match):
    return r"<p>" + match.groupdict()["content"].replace("\n", " ") + r"</p>"


def a_tag(match):
    return r"<a href=" + match.groupdict()["link"] + r">" + match.groupdict()["content"] + r"</a>"
