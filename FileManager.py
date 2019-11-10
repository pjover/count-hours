import logging
import os
import shutil
from itertools import count
from os.path import splitext


class FileManager:
    def __init__(self, file_path: str, backup_folder: str):
        self._file_path = os.path.abspath(file_path)
        if not os.path.exists(self._file_path):
            raise Exception('File {} not found'.format(self._file_path))
        logging.debug('Working with Markdown file %s', self._file_path)
        self._backup_folder = os.path.abspath(backup_folder)
        if not os.path.exists(self._backup_folder):
            raise Exception('Backup folder {} not found'.format(self._backup_folder))
        logging.debug('Working with backup folder %s', self._backup_folder)

    def load(self) -> list:
        file = open(self._file_path, 'r', encoding='utf-8')
        _lines = file.readlines()
        file.close()
        return _lines

    def save(self, _lines: list):
        self._backup()
        self._write_lines(_lines)

    def _backup(self):
        parts = os.path.split(self._file_path)
        backup_path = os.path.join(self._backup_folder, parts[1])
        path_and_filename, ext = splitext(backup_path)
        for counter in count():
            next_backup_file = '{0}-{1:03d}{2}'.format(path_and_filename, counter, ext)
            if not os.path.exists(next_backup_file):
                shutil.move(self._file_path, next_backup_file)
                logging.debug('Created backup file %s', next_backup_file)
                return

    def _write_lines(self, _lines: list):
        file = open(self._file_path, 'w', encoding='utf-8')
        for _line in _lines:
            file.write(_line)
        file.close()
        logging.debug('Updated file %s', self._file_path)
