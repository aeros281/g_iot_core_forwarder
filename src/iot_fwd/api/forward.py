""" Implement the hello command.

"""
from ..core.logger import logger


def main() -> str:
    """ Execute the command.

    :param name: name to use in greeting
    """
    logger.debug("executing forward command")
    return "Completed"
