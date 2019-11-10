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

regexp1 = re.compile('[(]([-+: 0-9]*)[)]')
regexp2 = re.compile('([0-2][0-9]:[0-5][0-9])-([0-2][0-9]:[0-5][0-9])')
regexp3 = re.compile('\[([.0-9]*)[ h\]]')
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
    for i in count():
        next_backup_file = '{0}-{1:03d}{2}'.format(path_and_filename, i, ext)
        if not os.path.exists(next_backup_file):
            shutil.move(file_path, next_backup_file)
            return next_backup_file


def save(file_path: str, _lines: list):
    with open(file_path, 'w', encoding='utf-8') as f:
        for _line in _lines:
            f.write(_line)


def read_current_month(line):
    return line[9:16]


def read_non_calculated_hours(line):
    total_time = None;

    result = regexp1.search(line)
    if result == None:
        return None

    else:
        segments = result.group(1).split('+')
        if DEBUG:
            print('Trobats: ', segments)
        for segment in segments:
            result = regexp2.search(segment)
            if result == None:
                return None

            start = result.group(1)
            end = result.group(2)
            delta_time = datetime.strptime(end, '%H:%M') - datetime.strptime(start, '%H:%M')
            if DEBUG:
                print('\tInici: {0}\tFinal: {1}\tDiferència: {2}'.format(start, end, delta_time))
            if (total_time):
                total_time = total_time + delta_time
            else:
                total_time = delta_time

    return total_time


def read_calculated_hours(line):
    result = regexp3.search(line)
    if result == None:
        return None

    else:
        f = float(result.group(1))
        if DEBUG:
            print('Trobat: ', f)
        return f


if __name__ == "__main__":
    try:
        input_file_name = sys.argv[1]
    except IndexError:
        print('Asumint que el fitxer per defecte és "{0}'.format(DEFAULT_FILE_NAME))
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
                sys.exit('Error: no se por interpretar el format de la linia "{0}"'.format(line))

            # Convertim el temps a format decimal
            hexa_time = str(total_time)
            splitted_time = hexa_time.split(':')
            decimal_time = int(splitted_time[0]) + (int(splitted_time[1]) / 60)
            formatted_time = '{0} [{1:0.2f} h]'.format(hexa_time, decimal_time)
            print('Afegides {0:0.2f} hores'.format(decimal_time))

            # Actualitza ses hores del mes en curs
            months[current_month] = months.get(current_month, 0) + decimal_time

            # Substitueix el simbol ? per el temps calculat
            modified_lines += 1
            lines[i] = line.replace('?', formatted_time)

        elif line.startswith('Hours: '):
            # Llegeix ses hores ja calculades per al resum
            decimal_time = read_calculated_hours(line)

            if decimal_time is None:
                sys.exit('Error: no se por interpretar el format de la linia "{0}"'.format(line))
            else:
                print("Ja n'hi havien {0:0.2f} hores".format(decimal_time))

                # Actualitza ses hores del mes en curs
                months[current_month] = months.get(current_month, 0) + decimal_time

    # Escriu el resumen
    lines = lines[: summary_line_index]
    lines.append('\n# Summary:\n')
    for month in months:
        lines.append('\t- {0} = {1:0.2f} h\n'.format(month, months.get(month, 0)))

    if (modified_lines == 0):
        print("No hi han canvis a processar")
    else:
        backup(input_file_name)
        save(input_file_name, lines)
