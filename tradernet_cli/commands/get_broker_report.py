"""
@desc: Отримати звіт брокера.
"""
from collections import namedtuple
import json
import logging
import os
import re
import xml.dom.minidom as xml_minidom

from tradernet_cli.commands import directory_path_type, date_type


logger = logging.getLogger(__name__)
FILENAME_RE = re.compile(r'filename=("(.*)"|(.*))')
TIME_PERIOD_NAME_TO_TIME = {
    'morning': '08:40:00',
    'evening': '23:59:59',
}


def add_arguments(parser):
    parser.add_argument('--get_broker_report_format', '-gbr_format',
                        default='json',
                        choices=['json', 'html', 'xml', 'xls', 'pdf'],
                        type=str,
                        help='Формат результуючого файлу.')

    parser.add_argument('--get_broker_report_output_directory', '-gbr_out_dir',
                        default='.',
                        type=directory_path_type,
                        help='Шлях до директорії в якій буде збережено результат операції.')

    parser.add_argument('--get_broker_report_date_start', '-gbr_date_start',
                        default=None,
                        type=date_type,
                        help='Дата початку звіту. Формат: рррр-мм-дд.')

    parser.add_argument('--get_broker_report_date_end', '-gbr_date_end',
                        default=None,
                        type=date_type,
                        help='Дата кінця звіту. Формат: рррр-мм-дд.')

    parser.add_argument('--get_broker_report_time_period', '-gbr_time_period',
                        default='evening',
                        choices=TIME_PERIOD_NAME_TO_TIME.keys(),
                        type=str,
                        help='Часовий період ('
                             'morning - з 08:40:00 date_start по 08:40:00 date_end | '
                             'evening - з 23:59:59 date_start по 23:59:59 date_end)')


ResponseData = namedtuple('ResponseData', ['filename', 'content', 'filemode'])


def get_filename_from_content_disposition_header(response):
    assert 'Content-disposition' in response.headers
    match = re.findall(FILENAME_RE, response.headers['Content-disposition'])
    assert(bool(match))
    filename = match[0][1] or match[0][2].replace('\'. ', '').replace(' .\'', '')
    return filename


def get_response_data_json(response):
    js_content = response.json()
    report = js_content['report']

    client_code = report["plainAccountInfoData"]["client_code"]
    date_start = report["date_start"].replace(":", "_")
    date_end = report["date_end"].replace(":", "_")
    filename = f'{client_code}_{date_start}_{date_end}_.json'

    content = json.dumps(report, indent=2)
    return ResponseData(filename, content, 'w')


def get_response_data_xls_pdf(response):
    filename = get_filename_from_content_disposition_header(response)
    return ResponseData(filename, response.content, 'wb')


def get_response_data_xml(response):
    filename = get_filename_from_content_disposition_header(response)
    xml_tree = xml_minidom.parseString(response.json())
    content = xml_tree.toprettyxml()
    return ResponseData(filename, content, 'w')


def get_response_data_html(response):
    filename = get_filename_from_content_disposition_header(response)
    content = response.content.decode('utf-8')
    return ResponseData(filename, content, 'w')


GET_DATA_BY_FORMAT = {
    'json': get_response_data_json,
    'html': get_response_data_html,
    'xml': get_response_data_xml,
    'xls': get_response_data_xls_pdf,
    'pdf': get_response_data_xls_pdf,
}


def execute(client, arguments):
    cmd = 'getBrokerReport'

    file_format = arguments.get_broker_report_format
    if file_format not in GET_DATA_BY_FORMAT:
        logger.error(f'Unsupported file format: {file_format}.')
        return

    params = {
        'format': file_format,
    }

    date_arguments = [
        arguments.get_broker_report_date_start,
        arguments.get_broker_report_date_end,
    ]

    if any(date_arguments):
        if not all(date_arguments):
            missing_argument = 'get_broker_report_date_start' if not arguments.get_broker_report_date_start\
                               else 'get_broker_report_date_end'
            logger.error(f'Both date arguments must be given or none at all. Missing {missing_argument}.')
            return

        params['date_start'] = arguments.get_broker_report_date_start
        params['date_end'] = arguments.get_broker_report_date_end
        params['time_period'] = TIME_PERIOD_NAME_TO_TIME[arguments.get_broker_report_time_period]
    else:
        params['recent'] = 1

    response = client.send_request(cmd, params=params, version=client.V2)
    data = GET_DATA_BY_FORMAT[file_format](response)

    filename = os.path.join(arguments.get_broker_report_output_directory, data.filename)
    with open(filename, data.filemode) as file:
        file.write(data.content)
