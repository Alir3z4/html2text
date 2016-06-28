import optparse
import warnings

from html2text.compat import urllib
from html2text import HTML2Text, config, __version__
from html2text.utils import wrapwrite, wrap_read


def main():
    baseurl = ''

    class bcolors:  # pragma: no cover
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

    p = optparse.OptionParser(
        '%prog [(filename|url) [encoding]]',
        version='%prog ' + ".".join(map(str, __version__))
    )
    p.add_option(
        "--pad-tables",
        dest="pad_tables",
        action="store_true",
        default=config.PAD_TABLES,
        help="pad the cells to equal column width in tables"
    )
    p.add_option(
        "--no-wrap-links",
        dest="wrap_links",
        action="store_false",
        default=config.WRAP_LINKS,
        help="wrap links during conversion"
    )
    p.add_option(
        "--ignore-emphasis",
        dest="ignore_emphasis",
        action="store_true",
        default=config.IGNORE_EMPHASIS,
        help="don't include any formatting for emphasis"
    )
    p.add_option(
        "--reference-links",
        dest="inline_links",
        action="store_false",
        default=config.INLINE_LINKS,
        help="use reference style links instead of inline links"
    )
    p.add_option(
        "--ignore-links",
        dest="ignore_links",
        action="store_true",
        default=config.IGNORE_ANCHORS,
        help="don't include any formatting for links")
    p.add_option(
        "--protect-links",
        dest="protect_links",
        action="store_true",
        default=config.PROTECT_LINKS,
        help=("protect links from line breaks surrounding them " +
              "with angle brackets"))
    p.add_option(
        "--ignore-images",
        dest="ignore_images",
        action="store_true",
        default=config.IGNORE_IMAGES,
        help="don't include any formatting for images"
    )
    p.add_option(
        "--images-to-alt",
        dest="images_to_alt",
        action="store_true",
        default=config.IMAGES_TO_ALT,
        help="Discard image data, only keep alt text"
    )
    p.add_option(
        "--images-with-size",
        dest="images_with_size",
        action="store_true",
        default=config.IMAGES_WITH_SIZE,
        help="Write image tags with height and width attrs as raw html to "
             "retain dimensions"
    )
    p.add_option(
        "-g", "--google-doc",
        action="store_true",
        dest="google_doc",
        default=False,
        help="convert an html-exported Google Document"
    )
    p.add_option(
        "-d", "--dash-unordered-list",
        action="store_true",
        dest="ul_style_dash",
        default=False,
        help="use a dash rather than a star for unordered list items"
    )
    p.add_option(
        "-e", "--asterisk-emphasis",
        action="store_true",
        dest="em_style_asterisk",
        default=False,
        help="use an asterisk rather than an underscore for emphasized text"
    )
    p.add_option(
        "-b", "--body-width",
        dest="body_width",
        action="store",
        type="int",
        default=config.BODY_WIDTH,
        help="number of characters per output line, 0 for no wrap"
    )
    p.add_option(
        "-i", "--google-list-indent",
        dest="list_indent",
        action="store",
        type="int",
        default=config.GOOGLE_LIST_INDENT,
        help="number of pixels Google indents nested lists"
    )
    p.add_option(
        "-s", "--hide-strikethrough",
        action="store_true",
        dest="hide_strikethrough",
        default=False,
        help="hide strike-through text. only relevant when -g is "
             "specified as well"
    )
    p.add_option(
        "--escape-all",
        action="store_true",
        dest="escape_snob",
        default=False,
        help="Escape all special characters.  Output is less readable, but "
             "avoids corner case formatting issues."
    )
    p.add_option(
        "--bypass-tables",
        action="store_true",
        dest="bypass_tables",
        default=config.BYPASS_TABLES,
        help="Format tables in HTML rather than Markdown syntax."
    )
    p.add_option(
        "--ignore-tables",
        action="store_true",
        dest="ignore_tables",
        default=config.IGNORE_TABLES,
        help="Ignore table-related tags (table, th, td, tr) while keeping rows."
    )
    p.add_option(
        "--single-line-break",
        action="store_true",
        dest="single_line_break",
        default=config.SINGLE_LINE_BREAK,
        help=(
            "Use a single line break after a block element rather than two "
            "line breaks. NOTE: Requires --body-width=0"
        )
    )
    p.add_option(
        "--unicode-snob",
        action="store_true",
        dest="unicode_snob",
        default=config.UNICODE_SNOB,
        help="Use unicode throughout document"
    )
    p.add_option(
        "--no-automatic-links",
        action="store_false",
        dest="use_automatic_links",
        default=config.USE_AUTOMATIC_LINKS,
        help="Do not use automatic links wherever applicable"
    )
    p.add_option(
        "--no-skip-internal-links",
        action="store_false",
        dest="skip_internal_links",
        default=config.SKIP_INTERNAL_LINKS,
        help="Do not skip internal links"
    )
    p.add_option(
        "--links-after-para",
        action="store_true",
        dest="links_each_paragraph",
        default=config.LINKS_EACH_PARAGRAPH,
        help="Put links after each paragraph instead of document"
    )
    p.add_option(
        "--mark-code",
        action="store_true",
        dest="mark_code",
        default=config.MARK_CODE,
        help="Mark program code blocks with [code]...[/code]"
    )
    p.add_option(
        "--decode-errors",
        dest="decode_errors",
        action="store",
        type="string",
        default=config.DECODE_ERRORS,
        help="What to do in case of decode errors.'ignore', 'strict' and 'replace' are acceptable values"
    )
    (options, args) = p.parse_args()

    # process input
    encoding = "utf-8"
    if len(args) == 2:
        encoding = args[1]
    elif len(args) > 2:
        p.error('Too many arguments')

    if len(args) > 0 and args[0] != '-':  # pragma: no cover
        file_ = args[0]

        if file_.startswith('http://') or file_.startswith('https://'):
            warnings.warn("Support for retrieving html over network is set for deprecation by version (2017, 1, x)",
                    DeprecationWarning)
            baseurl = file_
            j = urllib.urlopen(baseurl)
            data = j.read()
            if encoding is None:
                try:
                    from feedparser import _getCharacterEncoding as enc
                except ImportError:
                    enc = lambda x, y: ('utf-8', 1)
                encoding = enc(j.headers, data)[0]
                if encoding == 'us-ascii':
                    encoding = 'utf-8'
        else:
            data = open(file_, 'rb').read()
            if encoding is None:
                try:
                    from chardet import detect
                except ImportError:
                    detect = lambda x: {'encoding': 'utf-8'}
                encoding = detect(data)['encoding']
    else:
        data = wrap_read()

    if hasattr(data, 'decode'):
        try:
            try:
                data = data.decode(encoding, errors=options.decode_errors)
            except TypeError:
                # python 2.6.x does not have the errors option
                data = data.decode(encoding)
        except UnicodeDecodeError as err:
            warning = bcolors.WARNING + "Warning:" + bcolors.ENDC
            warning += ' Use the ' + bcolors.OKGREEN
            warning += '--decode-errors=ignore' + bcolors.ENDC + 'flag.'
            print(warning)
            raise err

    h = HTML2Text(baseurl=baseurl)
    # handle options
    if options.ul_style_dash:
        h.ul_item_mark = '-'
    if options.em_style_asterisk:
        h.emphasis_mark = '*'
        h.strong_mark = '__'

    h.body_width = options.body_width
    h.google_list_indent = options.list_indent
    h.ignore_emphasis = options.ignore_emphasis
    h.ignore_links = options.ignore_links
    h.protect_links = options.protect_links
    h.ignore_images = options.ignore_images
    h.images_to_alt = options.images_to_alt
    h.images_with_size = options.images_with_size
    h.google_doc = options.google_doc
    h.hide_strikethrough = options.hide_strikethrough
    h.escape_snob = options.escape_snob
    h.bypass_tables = options.bypass_tables
    h.ignore_tables = options.ignore_tables
    h.single_line_break = options.single_line_break
    h.inline_links = options.inline_links
    h.unicode_snob = options.unicode_snob
    h.use_automatic_links = options.use_automatic_links
    h.skip_internal_links = options.skip_internal_links
    h.links_each_paragraph = options.links_each_paragraph
    h.mark_code = options.mark_code
    h.wrap_links = options.wrap_links
    h.pad_tables = options.pad_tables

    wrapwrite(h.handle(data))
