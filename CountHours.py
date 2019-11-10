#! /usr/bin/env python3
import os
import re
import shutil
import sys
from datetime import datetime
from itertools import count
from os.path import splitext

DEBUG = False
DEFAULT_FILE_NAME = 'log.md'

BACKUP_FOLDER = 'log_backups'


def read_file(file_path: str) -> list:
    with open(file_path, 'r', encoding='utf-8') as f:
        _lines = f.readlines()
    return _lines


def backup(file_path: str):
    if not os.path.exists(file_path):
        raise Exception('File {} not found'.format(file_path))

    parts = os.path.split(file_path)
    backup_folder = os.path.join(parts[0], BACKUP_FOLDER)
    if not os.path.exists(backup_folder):
        raise Exception('Backup folder {} not found'.format(backup_folder))

    backup_path = os.path.join(backup_folder, parts[1])
    path_and_filename, ext = splitext(backup_path)
    for counter in count():
        next_backup_file = '{0}-{1:03d}{2}'.format(path_and_filename, counter, ext)
        if not os.path.exists(next_backup_file):
            shutil.move(file_path, next_backup_file)
            return next_backup_file


def save(file_path: str, _lines: list):
    with open(file_path, 'w', encoding='utf-8') as f:
        for _line in _lines:
            f.write(_line)


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
        if DEBUG:
            print('Found: ', segments)
        for segment in segments:
            result = parse_non_calculated_hours_segment.search(segment)
            if not result:
                return None

            start = result.group(1)
            end = result.group(2)
            delta_time = datetime.strptime(end, '%H:%M') - datetime.strptime(start, '%H:%M')
            if DEBUG:
                print('\tStart: {0}\tEnd: {1}\tDifference: {2}'.format(start, end, delta_time))
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
        if DEBUG:
            print('Found: ', f)
        return f


if __name__ == "__main__":
    try:
        input_file_name = sys.argv[1]
    except IndexError:
        print('The data file will be "{0}'.format(DEFAULT_FILE_NAME))
        input_file_name = DEFAULT_FILE_NAME

    lines = read_file(input_file_name)

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
            print('Added {0:0.2f} Hours'.format(decimal_time))

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
                print("There were already {0:0.2f} hours".format(decimal_time))

                # Actualitza ses hores del mes en curs
                months[current_month] = months.get(current_month, 0) + decimal_time

    # Escriu el resumen
    lines = lines[: summary_line_index]
    lines.append('# Summary:\n')
    for month in months:
        lines.append('\t- {0} = {1:0.2f} h\n'.format(month, months.get(month, 0)))

    if not modified_lines:
        print("No changes to process")
    else:
        backup(input_file_name)
        save(input_file_name, lines)
