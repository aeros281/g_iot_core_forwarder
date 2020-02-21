""" Implementation of the command line interface.

"""
from argparse import ArgumentParser
from inspect import getfullargspec

from . import __version__

from .api.hello import main as hello
from .api.forward import main as forward

from .core.config import config
from .core.logger import logger


__all__ = "main",


def main(argv=None) -> int:
    """ Execute the application CLI.

    :param argv: argument list to parse (sys.argv by default)
    :return: exit status
    """
    args = _args(argv)

    log_level = "WARN"
    if (args.debug):
        log_level = "DEBUG"

    logger.start(log_level)  # can't use default from config yet
    logger.debug("starting execution")

    config.load(args.config)
    config.core.config = args.config

    logger.stop()  # clear handlers to prevent duplicate records
    logger.start(config.core.logging)
    command = args.command
    args = vars(args)
    spec = getfullargspec(command)
    if not spec.varkw:
        # No kwargs, remove unexpected arguments.
        args = {key: args[key] for key in args if key in spec.args}
    try:
        command(**args)
    except RuntimeError as err:
        logger.critical(err)
        return 1
    logger.debug("successful completion")
    return 0


def _args(argv):
    """ Parse command line arguments.

    :param argv: argument list to parse
    """
    parser = ArgumentParser(
        description="CLI tool to create a MQTT forward to Google IoT Core"
    )
    parser.add_argument("-c", "--config", action="append",
                        help="config file [etc/config.yml]")
    parser.add_argument("-v", "--version", action="version",
                        version="iot_fwd {:s}".format(__version__),
                        help="print version and exit")
    parser.add_argument("-d", "--debug", action="store_true",
                        default=False,
                        help="enable debug logging")

    common = ArgumentParser(add_help=False)  # common subcommand arguments
    # common.add_argument(
    #    "--name", "-n", default="World", help="greeting name")

    subparsers = parser.add_subparsers(title="subcommands")
    _forward(subparsers, common)
    _hello(subparsers, common)

    args = parser.parse_args(argv)
    if not args.config:
        # Don't specify this as an argument default or else it will always be
        # included in the list.
        args.config = "etc/config.yml"
    return args


def _hello(subparsers, common):
    """ CLI adaptor for the api.hello command.

    :param subparsers: subcommand parsers
    :param common: parser for common subcommand arguments
    """
    parser = subparsers.add_parser("hello", parents=[common])

    parser.set_defaults(command=hello)
    return


def _forward(subparsers, common):
    """ CLI adaptor for the api.hello command.

    :param subparsers: subcommand parsers
    :param common: parser for common subcommand arguments
    """
    parser = subparsers.add_parser("forward", parents=[common])

    parser.add_argument("--cloud-service", choices=["Google", "AWS"],
                        help="target cloud service",
                        default="Google")

    parser.set_defaults(command=forward)
    return


# Make the module executable.

if __name__ == "__main__":
    try:
        status = main()
    except:
        logger.critical("shutting down due to fatal error")
        raise  # print stack trace
    else:
        raise SystemExit(status)
