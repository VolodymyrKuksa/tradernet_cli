"""
@desc: Отримати поточну позицію.
"""
import json


def add_arguments(parser):
    parser.add_argument(
        '--get_my_position_output_filename', '-gmp_out',
        default='./my_position.json',
        type=str,
        help='Розміщення та назва результуючого файлу команди get_my_position.')


def execute(client, arguments):
    cmd = 'getPositionJson'
    output_file = arguments.get_my_position_output_filename

    response = client.send_request(cmd, version=client.V2).json()
    response.raise_for_status()
    with open(output_file, "w") as file:
        json.dump(response, file, indent=2)
