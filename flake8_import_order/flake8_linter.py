from __future__ import absolute_import

import optparse

from flake8_import_order import __version__
from flake8_import_order.checker import (
    DEFAULT_IMPORT_ORDER_STYLE, ImportOrderChecker,
)


class Linter(ImportOrderChecker):
    name = "import-order"
    version = __version__

    def __init__(self, tree, filename):
        super(Linter, self).__init__(filename, tree)

    @classmethod
    def add_options(cls, parser):
        # List of application import names. They go last.
        register_opt(
            parser,
            "--application-import-names",
            default="",
            action="store",
            type="string",
            help="Import names to consider as application specific",
            parse_from_config=True,
            comma_separated_list=True,
        )
        register_opt(
            parser,
            "--import-order-style",
            default=DEFAULT_IMPORT_ORDER_STYLE,
            action="store",
            type="string",
            help=("Style to follow. Available: "
                  "cryptography, google, smarkets, pep8"),
            parse_from_config=True,
        )

    @classmethod
    def parse_options(cls, options):
        optdict = {}

        names = options.application_import_names
        if not isinstance(names, list):
            names = options.application_import_names.split(",")

        optdict = dict(
            application_import_names=[n.strip() for n in names],
            import_order_style=options.import_order_style,
        )

        cls.options = optdict

    def error(self, error):
        return (
            error.lineno,
            0,
            "{0} {1}".format(error.code, error.message),
            Linter,
        )

    def run(self):
        for error in self.check_order():
            yield error


def register_opt(parser, *args, **kwargs):
    try:
        # Flake8 3.x registration
        parser.add_option(*args, **kwargs)
    except (optparse.OptionError, TypeError):
        # Flake8 2.x registration
        parse_from_config = kwargs.pop('parse_from_config', False)
        kwargs.pop('comma_separated_list', False)
        kwargs.pop('normalize_paths', False)
        parser.add_option(*args, **kwargs)
        if parse_from_config:
            parser.config_options.append(args[-1].lstrip('-'))
