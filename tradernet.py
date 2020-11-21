import argparse
import importlib
import logging

from tradernet_client import PublicApiClient as TNClient
import commands


logger = logging.getLogger(__name__)


class ArgparseFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter):
    pass


# ф-ція для зчитування аргументів програми
def parse_arguments():
    parser = argparse.ArgumentParser(
        description='http клієнт для TraderNet',
        formatter_class=ArgparseFormatter
    )

    cyprus_api_url = 'https://tradernet.com/api'
    parser.add_argument('--api_url', '-au', default=cyprus_api_url, type=str,
                        help=f'URL для TraderNet API (Кіпр - {cyprus_api_url}, Беліз - ???)')

    parser.add_argument('--public_key', '-pk', required=True, type=str, help='Ваш публічний ключ TraderNet API')
    parser.add_argument('--secret', '-s', required=True, type=str, help='Ваш секрет TraderNet API')

    commands.add_arguments(parser)

    return parser.parse_args()


# точка входу
if __name__ == '__main__':
    arguments = parse_arguments()
    client = TNClient(arguments.api_url, arguments.public_key, arguments.secret)
    try:
        command = importlib.import_module(f'commands.{arguments.command}')
        command.execute(client, arguments)
    except ModuleNotFoundError:
        logger.error(f'Command "{arguments.command}" is not supported.')
