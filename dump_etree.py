# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
__version__ = '1.0'

import sys
import argparse
import traceback
from lxml import etree


def dump_etree(node, parent=None, out=None, without_text=False, ignore_script=True):
    out = out or sys.stdout
    if ignore_script and node.tag == 'script':
        return

    here = list(parent or [''])
    here.append(node.tag)
    path = '/'.join(here)
    print >>out, path
    for attname, value in node.items():
        if attname == 'class':
            for class_name in value.split():
                print >>out, '{}@{}={}'.format(path, attname, class_name)
        else:
            print >>out, '{}@{}={}'.format(path, attname, value)
    for child in node.xpath('child::node()'):
        if type(child).__name__ == '_Comment':
            print >>out, '/! {}'.format(child.text.strip())
            continue

        if hasattr(child, 'tag') and not hasattr(child.tag, '__call__'):
            dump_etree(
                child,
                out=out,
                parent=here,
                without_text=without_text,
                ignore_script=ignore_script,
                )
            continue

        if without_text or not unicode(child).strip():
            continue

        print >>out, child


class Command(object):
    PROG = __name__
    VERSION = __version__

    def add_parser_argument(self, parser):
        parser.set_defaults(input_format='html')

        parser.add_argument(
            '--xml',
            action='store_const', dest='input_format', const='xml',
            )

        parser.add_argument(
            '--html',
            action='store_const', dest='input_format', const='html',
            )

        parser.add_argument(
            '--encoding',
            action='store', dest='encoding', default='utf-8',
            )

        parser.add_argument(
            '--no-text',
            action='store_true', dest='without_text', default=False,
            )

        parser.add_argument(
            '--script',
            action='store_false', dest='ignore_script', default=True,
            )

        parser.add_argument(
            '--traceback', action='store_true',
            help=u"traceback on exception",
            )

        parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s version {}'.format(self.VERSION),
            )

    @classmethod
    def main(cls):
        try:
            sys.exit(cls().run_from_argv(sys.argv))
        except KeyboardInterrupt:
            sys.exit(1)

    def run_from_argv(self, argv):
        parser = argparse.ArgumentParser(prog=self.PROG)
        self.add_parser_argument(parser)
        options, args = parser.parse_known_args(argv[1:])

        try:
            self.stderr = getattr(options, 'stderr', sys.stderr)
            return self.handle(*args, **options.__dict__)
        except Exception as err:
            if options.traceback:
                self.stderr.write(traceback.format_exc())
            else:
                self.stderr.write("{}: {}\n".format(type(err).__name__, err))
            sys.exit(1)

    def handle(self, *args, **options):
        encoding = options.get('encoding')

        for infile in args or (sys.stdin,):
            if infile == '-':
                infile = sys.stdin

            parser_class = etree.XMLParser if options.get('input_format') == 'xml' else etree.HTMLParser
            parser = parser_class(encoding=encoding)
            tree = etree.parse(infile, parser=parser)
            dump_etree(tree.getroot(),
                       out=options.get('stdout'),
                       without_text=options.get('without_text', False),
                       ignore_script=options.get('ignore_script', True),
                       )


if __name__ == '__main__':
    Command.main()
