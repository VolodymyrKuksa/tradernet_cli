from collections import namedtuple
import importlib
import logging
import os
from pathlib import Path
import re


logger = logging.getLogger(__name__)

DESCRIPTION_RE = re.compile(r'.*@desc:\s*(.*)\n')
DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
Command = namedtuple('Command', ['name', 'description'])


def directory_path_type(value):
    if os.path.isdir(value):
        return value
    else:
        raise NotADirectoryError(value)


def date_type(value):
    if type(value) != str or not re.fullmatch(DATE_RE, value):
        raise ValueError(f'Invalid date format: {value}.')
    return value


def parse_available_commands():
    available_commands = []

    commands_directory = Path(os.path.split(__file__)[0])
    command_file_paths = [filepath for filepath in commands_directory.glob('*.py') if not filepath.name.startswith('_')]

    for path in command_file_paths:
        text = path.read_text()
        match = re.findall(DESCRIPTION_RE, text)

        if not match:
            logger.error(f'Missing "@desc:" for file "{path}". Ignoring this command.')
            continue

        available_commands.append(Command(path.name[:-3], match[0]))

    return available_commands


def add_arguments(parser):
    available_commands = parse_available_commands()
    commands_help = '\n'.join([f'{command.name} - {command.description}' for command in available_commands])

    parser.add_argument('command', type=str, choices=[command.name for command in available_commands],
                        help=f'Команда для виконання. Наявні команди:\n{commands_help}')

    for command in available_commands:
        command_module = importlib.import_module(f'tradernet_cli.commands.{command.name}')
        if 'add_arguments' in command_module.__dict__.keys():
            command_module.add_arguments(parser)
