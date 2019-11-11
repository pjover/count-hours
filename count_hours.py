#! /usr/bin/env python3

import argparse
import logging

from FileManager import FileManager
from MarkdownProcessor import MarkdownProcessor


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", type=str, help="The Markdown file to process")
    parser.add_argument("-bf", "--backup_folder", type=str, help="Folder to store the backups", default='log_backups')
    parser.add_argument("-d", "--debug", help="Shows all the DEBUG level logging messages", action='store_true')
    _args = parser.parse_args()
    if _args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.info('Showing all the DEBUG level logging messages')
    else:
        logging.getLogger().setLevel(logging.INFO)
    return _args


if __name__ == "__main__":
    args = parse_arguments()

    file_manager = FileManager(args.file_path, args.backup_folder)
    processor = MarkdownProcessor()
    lines = processor.process(file_manager.load())

    if processor.has_changed():
        file_manager.save(lines)
    else:
        logging.info("No changes to process")
