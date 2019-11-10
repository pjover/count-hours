from unittest.mock import MagicMock, call

from assertpy import assert_that
from pytest import raises

from CountHours import read_current_month, read_non_calculated_hours, read_calculated_hours, backup


def test_backup(monkeypatch):
    mock_exists = MagicMock(side_effect=[True, True, False])
    monkeypatch.setattr('os.path.exists', mock_exists)
    mock_move = MagicMock()
    monkeypatch.setattr('shutil.move', mock_move)

    actual = backup('dir/filename.ext')

    mock_exists.assert_has_calls([
        call('dir/filename.ext'),
        call('dir/log_backups'),
        call('dir/log_backups/filename-000.ext')])
    mock_move.assert_called_once_with('dir/filename.ext', 'dir/log_backups/filename-000.ext')
    assert_that(actual).is_equal_to('dir/log_backups/filename-000.ext')


def test_backup_if_file_does_not_exists(monkeypatch):
    mock_exists = MagicMock(return_value=False)
    monkeypatch.setattr('os.path.exists', mock_exists)
    with raises(Exception):
        backup('dir/filename.ext')
    mock_exists.assert_called_once_with('dir/filename.ext')


def test_backup_if_backup_folder_does_not_exists(monkeypatch):
    mock_exists = MagicMock(side_effect=[True, False])
    monkeypatch.setattr('os.path.exists', mock_exists)
    with raises(Exception):
        backup('dir/filename.ext')
    mock_exists.assert_has_calls([call('dir/filename.ext'), call('dir/log_backups')])


def test_read_current_month():
    assert_that(read_current_month('## Date: 2013-08-10\n')).is_equal_to('2013-08')
    assert_that(read_current_month('## Date: 2013-08-10\n')).is_not_equal_to('2013-08-10')


def test_read_non_calculated_hours():
    assert_that(str(read_non_calculated_hours('Hours: ? (16:00-16:20 + 19:00-20:30)\n'))).is_equal_to('1:50:00')
    assert_that(str(read_non_calculated_hours('Hours: ? (16:00-16:20 + 19:00-20:30)\n'))).is_not_equal_to('1:50')


def test_read_calculated_hours():
    assert_that(read_calculated_hours('Hours: 1:50:00 [1.83 h] (16:00-16:20 + 19:00-20:30)\n')).is_equal_to(1.83)
    assert_that(read_calculated_hours('Hours: 1:50:00 [1.83 h] (16:00-16:20 + 19:00-20:30)\n')).is_not_equal_to(1.833)
