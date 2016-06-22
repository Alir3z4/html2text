import sys

from html2text import config
from html2text.compat import htmlentitydefs


def name2cp(k):
    """Return sname to codepoint"""
    if k == 'apos':
        return ord("'")
    return htmlentitydefs.name2codepoint[k]


unifiable_n = {}

for k in config.UNIFIABLE.keys():
    unifiable_n[name2cp(k)] = config.UNIFIABLE[k]


def hn(tag):
    if tag[0] == 'h' and len(tag) == 2:
        try:
            n = int(tag[1])
            if n in range(1, 10):  # pragma: no branch
                return n
        except ValueError:
            return 0


def dumb_property_dict(style):
    """
    :returns: A hash of css attributes
    """
    out = dict([(x.strip().lower(), y.strip().lower()) for x, y in
                [z.split(':', 1) for z in
                 style.split(';') if ':' in z
                 ]
                ]
               )

    return out


def dumb_css_parser(data):
    """
    :type data: str

    :returns: A hash of css selectors, each of which contains a hash of
    css attributes.
    :rtype: dict
    """
    # remove @import sentences
    data += ';'
    importIndex = data.find('@import')
    while importIndex != -1:
        data = data[0:importIndex] + data[data.find(';', importIndex) + 1:]
        importIndex = data.find('@import')

    # parse the css. reverted from dictionary comprehension in order to
    # support older pythons
    elements = [x.split('{') for x in data.split('}') if '{' in x.strip()]
    try:
        elements = dict([(a.strip(), dumb_property_dict(b))
                         for a, b in elements])
    except ValueError:  # pragma: no cover
        elements = {}  # not that important

    return elements


def element_style(attrs, style_def, parent_style):
    """
    :type attrs: dict
    :type style_def: dict
    :type style_def: dict

    :returns: A hash of the 'final' style attributes of the element
    :rtype: dict
    """
    style = parent_style.copy()
    if 'class' in attrs:
        for css_class in attrs['class'].split():
            css_style = style_def.get('.' + css_class, {})
            style.update(css_style)
    if 'style' in attrs:
        immediate_style = dumb_property_dict(attrs['style'])
        style.update(immediate_style)

    return style


def google_list_style(style):
    """
    Finds out whether this is an ordered or unordered list

    :type style: dict

    :rtype: str
    """
    if 'list-style-type' in style:
        list_style = style['list-style-type']
        if list_style in ['disc', 'circle', 'square', 'none']:
            return 'ul'

    return 'ol'


def google_has_height(style):
    """
    Check if the style of the element has the 'height' attribute
    explicitly defined

    :type style: dict

    :rtype: bool
    """
    if 'height' in style:
        return True

    return False


def google_text_emphasis(style):
    """
    :type style: dict

    :returns: A list of all emphasis modifiers of the element
    :rtype: list
    """
    emphasis = []
    if 'text-decoration' in style:
        emphasis.append(style['text-decoration'])
    if 'font-style' in style:
        emphasis.append(style['font-style'])
    if 'font-weight' in style:
        emphasis.append(style['font-weight'])

    return emphasis


def google_fixed_width_font(style):
    """
    Check if the css of the current element defines a fixed width font

    :type style: dict

    :rtype: bool
    """
    font_family = ''
    if 'font-family' in style:
        font_family = style['font-family']
    if 'courier new' == font_family or 'consolas' == font_family:
        return True

    return False


def list_numbering_start(attrs):
    """
    Extract numbering from list element attributes

    :type attrs: dict

    :rtype: int or None
    """
    if 'start' in attrs:
        try:
            return int(attrs['start']) - 1
        except ValueError:
            pass

    return 0


def skipwrap(para, wrap_links):
    # If it appears to contain a link
    # don't wrap
    if (len(config.RE_LINK.findall(para)) > 0) and not wrap_links:
        return True
    # If the text begins with four spaces or one tab, it's a code block;
    # don't wrap
    if para[0:4] == '    ' or para[0] == '\t':
        return True

    # If the text begins with only two "--", possibly preceded by
    # whitespace, that's an emdash; so wrap.
    stripped = para.lstrip()
    if stripped[0:2] == "--" and len(stripped) > 2 and stripped[2] != "-":
        return False

    # I'm not sure what this is for; I thought it was to detect lists,
    # but there's a <br>-inside-<span> case in one of the tests that
    # also depends upon it.
    if stripped[0:1] == '-' or stripped[0:1] == '*':
        return True

    # If the text begins with a single -, *, or +, followed by a space,
    # or an integer, followed by a ., followed by a space (in either
    # case optionally proceeded by whitespace), it's a list; don't wrap.
    if config.RE_ORDERED_LIST_MATCHER.match(stripped) or \
            config.RE_UNORDERED_LIST_MATCHER.match(stripped):
        return True

    return False


def wrapwrite(text):
    text = text.encode('utf-8')
    try:  # Python3
        sys.stdout.buffer.write(text)
    except AttributeError:
        sys.stdout.write(text)


def wrap_read():  # pragma: no cover
    """
    :rtype: str
    """
    try:
        return sys.stdin.read()
    except AttributeError:
        return sys.stdin.buffer.read()


def escape_md(text):
    """
    Escapes markdown-sensitive characters within other markdown
    constructs.
    """
    return config.RE_MD_CHARS_MATCHER.sub(r"\\\1", text)


def escape_md_section(text, snob=False):
    """
    Escapes markdown-sensitive characters across whole document sections.
    """
    text = config.RE_MD_BACKSLASH_MATCHER.sub(r"\\\1", text)

    if snob:
        text = config.RE_MD_CHARS_MATCHER_ALL.sub(r"\\\1", text)

    text = config.RE_MD_DOT_MATCHER.sub(r"\1\\\2", text)
    text = config.RE_MD_PLUS_MATCHER.sub(r"\1\\\2", text)
    text = config.RE_MD_DASH_MATCHER.sub(r"\1\\\2", text)

    return text

def reformat_table(lines, right_margin):
    """
    Given the lines of a table
    padds the cells and returns the new lines
    """
    # find the maximum width of the columns
    max_width = [len(x.rstrip()) + right_margin for x in lines[0].split('|')]
    for line in lines:
        cols = [x.rstrip() for x in line.split('|')]
        max_width = [max(len(x) + right_margin, old_len)
                     for x, old_len in zip(cols, max_width)]
    
    # reformat
    new_lines = []
    for line in lines:
        cols = [x.rstrip() for x in line.split('|')]
        if set(line.strip()) == set('-|'):
            filler = '-'
            new_cols = [x.rstrip() + (filler * (M - len(x.rstrip())))
                        for x, M in zip(cols, max_width)]
        else:
            filler = ' '
            new_cols = [x.rstrip() + (filler * (M - len(x.rstrip())))
                        for x, M in zip(cols, max_width)]
        new_lines.append('|'.join(new_cols))
    return new_lines

def pad_tables_in_text(text, right_margin=1):
    """
    Provide padding for tables in the text
    """
    lines = text.split('\n')
    table_buffer, altered_lines, table_widths, table_started = [], [], [], False
    new_lines = []
    for line in lines:
        # Toogle table started
        if (config.TABLE_MARKER_FOR_PAD in line):
            table_started = not table_started
            if not table_started:
                table = reformat_table(table_buffer, right_margin)
                new_lines.extend(table)
                table_buffer = []
                new_lines.append('')
            continue
        # Process lines
        if table_started:
            table_buffer.append(line)
        else:
            new_lines.append(line)
    new_text = '\n'.join(new_lines)
    return new_text
