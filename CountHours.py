#! /usr/bin/env python3
import argparse
import logging
import re
import sys
from datetime import datetime

from FileManager import FileManager


def read_current_month(_line):
    return _line[9:16]


parse_non_calculated_hours_segments = re.compile(r'[(]([-+: 0-9]*)[)]')
parse_non_calculated_hours_segment = re.compile(r'([0-2][0-9]:[0-5][0-9])-([0-2][0-9]:[0-5][0-9])')


def read_non_calculated_hours(_line):
    _total_time = None

    result = parse_non_calculated_hours_segments.search(_line)
    if not result:
        return None

    else:
        segments = result.group(1).split('+')
        logging.debug('Found: %s', segments)
        for segment in segments:
            result = parse_non_calculated_hours_segment.search(segment)
            if not result:
                return None

            start = result.group(1)
            end = result.group(2)
            delta_time = datetime.strptime(end, '%H:%M') - datetime.strptime(start, '%H:%M')
            logging.debug('\tStart: %s\tEnd: %s\tDifference: %s', start, end, delta_time)
            if _total_time:
                _total_time = _total_time + delta_time
            else:
                _total_time = delta_time

    return _total_time


parse_calculated_hours = re.compile(r'\[([.0-9]*)[ h\]]')


def read_calculated_hours(_line):
    result = parse_calculated_hours.search(_line)
    if not result:
        return None

    else:
        f = float(result.group(1))
        logging.debug('Found: %f', f)
        return f


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", type=str, help="The Markdown file to process")
    parser.add_argument("-bf", "--backup_folder", type=str, help="Folder to store the backups", default='log_backups')
    parser.add_argument("-d", "--debug", help="Shows all the DEBUG level logging messages", action='store_true')
    args = parser.parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.info('Showing all the DEBUG level logging messages')
    else:
        logging.getLogger().setLevel(logging.INFO)
    return args


if __name__ == "__main__":
    args = parse_arguments()
    file_manager = FileManager(args.file_path, args.backup_folder)

    lines = file_manager.load()

    months = {}
    current_month = None
    modified_lines = 0
    summary_line_index = len(lines)
    for i, line in enumerate(lines):
        if line.startswith('# Summary'):
            summary_line_index = i
            break

        elif line.startswith('## Date: '):
            # Llegeix el mes
            current_month = read_current_month(line)

        elif line.startswith('Hours: ?'):
            # Llegeix ses hores sense calcular
            total_time = read_non_calculated_hours(line)
            if not total_time:
                sys.exit('Error in line format "{0}"'.format(line))

            # Convertim el temps a format decimal
            hexa_time = str(total_time)
            splitted_time = hexa_time.split(':')
            decimal_time = int(splitted_time[0]) + (int(splitted_time[1]) / 60)
            formatted_time = '{0} [{1:0.2f} h]'.format(hexa_time, decimal_time)
            logging.info('Added {0:0.2f} Hours'.format(decimal_time))

            # Actualitza ses hores del mes en curs
            months[current_month] = months.get(current_month, 0) + decimal_time

            # Substitueix el simbol ? per el temps calculat
            modified_lines += 1
            lines[i] = line.replace('?', formatted_time)

        elif line.startswith('Hours: '):
            # Llegeix ses hores ja calculades per al resum
            decimal_time = read_calculated_hours(line)

            if decimal_time is None:
                sys.exit('Error in line format "{0}"'.format(line))
            else:
                logging.info("There were already {0:0.2f} hours".format(decimal_time))

                # Actualitza ses hores del mes en curs
                months[current_month] = months.get(current_month, 0) + decimal_time

    # Escriu el resumen
    lines = lines[: summary_line_index]
    lines.append('# Summary:\n')
    for month in months:
        msg = '{0} = {1:0.2f} h'.format(month, months.get(month, 0))
        logging.info(msg)
        lines.append('\t- {0}\n'.format(msg))

    if not modified_lines:
        logging.info("No changes to process")
    else:
        file_manager.save(lines)
