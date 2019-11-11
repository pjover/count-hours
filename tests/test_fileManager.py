import logging
from unittest.mock import MagicMock, call

import pytest
from pytest import raises
from testfixtures import LogCapture

from FileManager import FileManager


def teardown_module():
    LogCapture.uninstall_all()


@pytest.fixture()
def log():
    return LogCapture(level=logging.DEBUG)


@pytest.fixture()
def os_path_abspath(monkeypatch):
    mock = MagicMock(side_effect=['dir/filename.ext', 'dir/log_backups'])
    monkeypatch.setattr('os.path.abspath', mock)
    return mock


@pytest.fixture()
def os_path_exists(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr('os.path.exists', mock)
    return mock


def test_init_ok(os_path_abspath, os_path_exists, log):
    os_path_exists.side_effect = [True, True]

    FileManager('dir/filename.ext', 'dir/log_backups')

    os_path_abspath.assert_has_calls([call('dir/filename.ext'), call('dir/log_backups')])
    os_path_exists.assert_has_calls([call('dir/filename.ext'), call('dir/log_backups')])
    log.check(
        ('root', 'DEBUG', 'Working with Markdown file dir/filename.ext'),
        ('root', 'DEBUG', 'Working with backup folder dir/log_backups')
    )


def test_init_ko_file_path(os_path_abspath, os_path_exists):
    os_path_exists.side_effect = [False, True]

    with raises(Exception):
        FileManager('dir/filename.ext', 'dir/log_backups')

    os_path_abspath.assert_called_once_with('dir/filename.ext')
    os_path_exists.assert_called_once_with('dir/filename.ext')


def test_init_ko_backup_folder(os_path_abspath, os_path_exists, log):
    os_path_exists.side_effect = [True, False]

    with raises(Exception):
        FileManager('dir/filename.ext', 'dir/log_backups')

    os_path_abspath.assert_has_calls([call('dir/filename.ext'), call('dir/log_backups')])
    os_path_exists.assert_has_calls([call('dir/filename.ext'), call('dir/log_backups')])
    log.check(
        ('root', 'DEBUG', 'Working with Markdown file dir/filename.ext')
    )


@pytest.fixture()
def sut(os_path_abspath, os_path_exists):
    os_path_exists.side_effect = [True, True]
    return FileManager('dir/filename.ext', 'dir/log_backups')


def test_load(monkeypatch, sut):
    expected = ['line 1', 'line 2']
    file_mock = MagicMock()
    file_mock.readlines = MagicMock(return_value=expected)
    open_mock = MagicMock(return_value=file_mock)
    monkeypatch.setattr('builtins.open', open_mock)

    actual = sut.load()

    assert actual == expected
    open_mock.assert_called_once_with('dir/filename.ext', 'r', encoding='utf-8')


def test_save(os_path_exists, monkeypatch, sut, log):
    os_path_exists.side_effect = [True, True, False]
    mock_move = MagicMock()
    monkeypatch.setattr('shutil.move', mock_move)
    file_mock = MagicMock()
    open_mock = MagicMock(return_value=file_mock)
    monkeypatch.setattr('builtins.open', open_mock)

    sut.save(['line 1', 'line 2'])

    os_path_exists.assert_has_calls([
        call('dir/filename.ext'),
        call('dir/log_backups'),
        call('dir/log_backups/filename-000.ext')])
    mock_move.assert_called_once_with('dir/filename.ext', 'dir/log_backups/filename-002.ext')
    open_mock.assert_called_once_with('dir/filename.ext', 'w', encoding='utf-8')
    log.check(
        ('root', 'DEBUG', 'Created backup file dir/log_backups/filename-002.ext'),
        ('root', 'DEBUG', 'Updated file dir/filename.ext')
    )
