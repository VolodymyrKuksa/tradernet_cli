import argparse
import copy
import importlib
import logging
import traceback

from tradernet_cli import configure_logging

from tradernet_cli.tradernet_client import PublicApiClient as TNClient
from tradernet_cli.tradernet_client import TraderNetAPIError
import tradernet_cli.commands as commands

logger = logging.getLogger(__name__)


class ArgparseFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter):
    pass


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='http клієнт для TraderNet',
        formatter_class=ArgparseFormatter
    )

    cyprus_api_url = 'https://tradernet.com/api'
    parser.add_argument('--api_url', '-au', default=cyprus_api_url, type=str,
                        help=f'URL для TraderNet API.')

    parser.add_argument('--public_key', '-pk', required=True, type=str, help='Ваш публічний ключ TraderNet API')
    parser.add_argument('--secret', '-s', required=True, type=str, help='Ваш секрет TraderNet API')

    commands.add_arguments(parser)

    return parser.parse_args()


def log_execution_info(arguments):
    args = copy.deepcopy(arguments)
    del args.public_key
    del args.secret
    logger.info(f'Trying to execute command "{args.command}" with arguments {args}')


if __name__ == '__main__':
    configure_logging()

    arguments = parse_arguments()
    client = TNClient(arguments.api_url, arguments.public_key, arguments.secret)
    try:
        log_execution_info(arguments)
        command = importlib.import_module(f'tradernet_cli.commands.{arguments.command}')
        command.execute(client, arguments)
    except ModuleNotFoundError:
        logger.error(f'Command "{arguments.command}" is not supported.')
    except TraderNetAPIError as e:
        logger.error(f'Call to TraderNet API resulted in an error: {e}\n{traceback.format_exc()}')
    except Exception as e:
        logger.error(f'Unexpected Exception: {e}\n{traceback.format_exc()}')
        raise
