import codecs
import glob
import os
import re
import subprocess
import sys

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest
import logging

logging.basicConfig(format='%(levelname)s:%(funcName)s:%(message)s',
                    level=logging.DEBUG)

import html2text


def test_module(fn, google_doc=False, **kwargs):
    h = html2text.HTML2Text()
    h.fn = fn

    if google_doc:
        h.google_doc = True
        h.ul_item_mark = '-'
        h.body_width = 0
        h.hide_strikethrough = True

    for k, v in kwargs.items():
        setattr(h, k, v)

    result = get_baseline(fn)
    inf = open(fn)
    actual = h.handle(inf.read())
    inf.close()
    return result, actual


def test_command(fn, *args):
    args = list(args)
    cmd = [sys.executable, '-m', 'html2text.__init__']

    if '--googledoc' in args:
        args.remove('--googledoc')
        cmd += ['-g', '-d', '-b', '0', '-s']

    if args:
        cmd.extend(args)

    cmd += [fn]

    result = get_baseline(fn)
    pid = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    out, _ = pid.communicate()

    actual = out.decode('utf8')

    if os.name == 'nt':
        # Fix the unwanted CR to CRCRLF replacement
        # during text pipelining on Windows/cygwin
        actual = re.sub(r'\r+', '\r', actual)
        actual = actual.replace('\r\n', '\n')

    return result, actual


def test_function(fn, **kwargs):
    with open(fn) as inf:
        actual = html2text.html2text(inf.read(), **kwargs)
    result = get_baseline(fn)
    return result, actual


def get_dump_name(fn, suffix):
    return '%s-%s_output.md' % (os.path.splitext(fn)[0], suffix)


def get_baseline_name(fn):
    return os.path.splitext(fn)[0] + '.md'


def get_baseline(fn):
    name = get_baseline_name(fn)
    f = codecs.open(name, mode='r', encoding='utf8')
    out = f.read()
    f.close()
    return out


class TestHTML2Text(unittest.TestCase):
    pass


def generate_test(fn):
    def test_mod(self):
        self.maxDiff = None
        result, actual = test_module(fn, **module_args)
        self.assertEqual(result, actual)

    def test_cmd(self):
        # Because there is no command-line option to control unicode_snob
        if 'unicode_snob' not in module_args:
            self.maxDiff = None
            result, actual = test_command(fn, *cmdline_args)
            self.assertEqual(result, actual)

    def test_func(self):
        result, actual = test_function(fn, **func_args)
        self.assertEqual(result, actual)

    module_args = {}
    cmdline_args = []
    func_args = {}
    base_fn = os.path.basename(fn).lower()

    if base_fn.startswith('google'):
        module_args['google_doc'] = True
        cmdline_args.append('--googledoc')

    if base_fn.find('unicode') >= 0:
        module_args['unicode_snob'] = True

    if base_fn.find('flip_emphasis') >= 0:
        module_args['emphasis_mark'] = '*'
        module_args['strong_mark'] = '__'
        cmdline_args.append('-e')

    if base_fn.find('escape_snob') >= 0:
        module_args['escape_snob'] = True
        cmdline_args.append('--escape-all')

    if base_fn.find('table_bypass') >= 0:
        module_args['bypass_tables'] = True
        cmdline_args.append('--bypass-tables')

    if base_fn.startswith('table_ignore'):
        module_args['ignore_tables'] = True
        cmdline_args.append('--ignore-tables')

    if base_fn.startswith('bodywidth'):
        # module_args['unicode_snob'] = True
        module_args['body_width'] = 0
        cmdline_args.append('--body-width=0')
        func_args['bodywidth'] = 0

    if base_fn.startswith('protect_links'):
        module_args['protect_links'] = True
        cmdline_args.append('--protect-links')

    if base_fn.startswith('images_to_alt'):
        module_args['images_to_alt'] = True
        cmdline_args.append('--images-to-alt')

    if base_fn.startswith('images_with_size'):
        module_args['images_with_size'] = True
        cmdline_args.append('--images-with-size')

    if base_fn.startswith('single_line_break'):
        module_args['body_width'] = 0
        cmdline_args.append('--body-width=0')
        module_args['single_line_break'] = True
        cmdline_args.append('--single-line-break')

    if base_fn.startswith('no_inline_links'):
        module_args['inline_links'] = False
        cmdline_args.append('--reference-links')

    if base_fn.startswith('no_wrap_links'):
        module_args['wrap_links'] = False
        cmdline_args.append('--no-wrap-links')

    if base_fn.startswith('mark_code'):
        module_args['mark_code'] = True
        cmdline_args.append('--mark-code')

    if base_fn.startswith('pad_table'):
        module_args['pad_tables'] = True
        cmdline_args.append('--pad-tables')

    if base_fn not in ['bodywidth_newline.html', 'abbr_tag.html']:
        test_func = None

    if base_fn == 'inplace_baseurl_substitution.html':
        module_args['baseurl'] = 'http://brettterpstra.com'
        module_args['body_width'] = 0
        # there is no way to specify baseurl in cli :(
        test_cmd = None

    return test_mod, test_cmd, test_func

# Originally from http://stackoverflow.com/questions/32899/\
#    how-to-generate-dynamic-parametrized-unit-tests-in-python
test_dir_name = os.path.dirname(os.path.realpath(__file__))
for fn in glob.glob("%s/*.html" % test_dir_name):
    test_name = 'test_%s' % os.path.splitext(os.path.basename(fn))[0].lower()
    test_m, test_c, test_func = generate_test(fn)
    setattr(TestHTML2Text, test_name + "_mod", test_m)
    if test_c:
        setattr(TestHTML2Text, test_name + "_cmd", test_c)
    if test_func:
        setattr(TestHTML2Text, test_name + "_func", test_func)

if __name__ == "__main__":
    unittest.main()
