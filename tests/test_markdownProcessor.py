import logging

import pytest
from testfixtures import LogCapture

from MarkdownProcessor import MarkdownProcessor


def teardown_module():
    LogCapture.uninstall_all()


@pytest.fixture()
def log():
    return LogCapture(level=logging.DEBUG)


@pytest.fixture()
def sut():
    return MarkdownProcessor()


def test_process_without_changes(sut, log):
    lines = [
        '# To do:\n',
        '- Some pending tasks\n',
        '# Actions:\n',
        '## Date: 2014-01-17\n',
        'Hours: 0:38:00 [0.63 h] {16:18-16:38 + 16:41-16:59 - 19:00-19:20}\n',
        '- Watermark with logo\n',
        '- Credits\n',
        '# Summary:\n',
        '- 2014-01 = 0.63 h\n'
    ]
    actual = sut.process(lines)
    has_changed = sut.has_changed()

    assert actual == lines
    assert not has_changed
    log.check(
        ('root', 'DEBUG', 'Processing 9 lines'),
        ('root', 'INFO', 'There were already 0.63 hours'),
        ('root', 'INFO', '2014-01 = 0.63 h'),
        ('root', 'DEBUG', 'There are 0 modified lines')
    )


def test_process_with_changes(sut, log):
    lines = [
        '# To do:\n',
        '- Some pending tasks\n',
        '# Actions:\n',
        '## Date: 2014-02-10\n',
        'Hours: ? {18:43-18:46 + 21:41-22:25}\n',
        '- Check and tag\n',
        '- Export and upload\n',
        '## Date: 2014-01-20\n',
        'Hours: ? {17:10-19:30}\n',
        '- Editing video\n',
        '- Sound normalization\n',
        '- Color grading\n',
        '## Date: 2014-01-17\n',
        'Hours: 0:38:00 [0.63 h] {16:18-16:38 + 16:41-16:59 - 19:00-19:20}\n',
        '- Watermark with logo\n',
        '- Credits\n',
        '# Summary:\n',
        '- 2014-01 = 0.63 h\n'
    ]
    actual = sut.process(lines)
    has_changed = sut.has_changed()

    expected = [
        '# To do:\n',
        '- Some pending tasks\n',
        '# Actions:\n',
        '## Date: 2014-02-10\n',
        'Hours: 0:47:00 [0.78 h] {18:43-18:46 + 21:41-22:25}\n',
        '- Check and tag\n',
        '- Export and upload\n',
        '## Date: 2014-01-20\n',
        'Hours: 2:20:00 [2.33 h] {17:10-19:30}\n',
        '- Editing video\n',
        '- Sound normalization\n',
        '- Color grading\n',
        '## Date: 2014-01-17\n',
        'Hours: 0:38:00 [0.63 h] {16:18-16:38 + 16:41-16:59 - 19:00-19:20}\n',
        '- Watermark with logo\n',
        '- Credits\n',
        '# Summary:\n',
        '- 2014-02 = 0.78 h\n',
        '- 2014-01 = 2.96 h\n'
    ]
    assert actual == expected
    assert has_changed
    log.check(
        ('root', 'DEBUG', 'Processing 18 lines'),
        ('root', 'DEBUG', "Found: ['18:43-18:46 ', ' 21:41-22:25']"),
        ('root', 'DEBUG', '\tStart: 18:43\tEnd: 18:46\tDelta: 0:03:00'),
        ('root', 'DEBUG', '\tStart: 21:41\tEnd: 22:25\tDelta: 0:44:00'),
        ('root', 'INFO', 'Added 0.78 Hours'),
        ('root', 'DEBUG', "Found: ['17:10-19:30']"),
        ('root', 'DEBUG', '\tStart: 17:10\tEnd: 19:30\tDelta: 2:20:00'),
        ('root', 'INFO', 'Added 2.33 Hours'),
        ('root', 'INFO', 'There were already 0.63 hours'),
        ('root', 'INFO', '2014-02 = 0.78 h'),
        ('root', 'INFO', '2014-01 = 2.96 h'),
        ('root', 'DEBUG', 'There are 2 modified lines')
    )


def test_parse_current_month(sut, log):
    assert sut.parse_current_month('## Date: 2013-08-10\n') == '2013-08'
    assert sut.parse_current_month('## Date: 2013-08-10\n') != '2013-08-10'
    log.check(
    )


def test_parse_non_calculated_hours(sut, log):
    assert str(sut.parse_non_calculated_hours('Hours: ? {16:00-16:20 + 19:00-20:30}\n')) == '1:50:00'
    assert str(sut.parse_non_calculated_hours('Hours: ? {16:00-16:20 + 19:00-20:30}\n')) != '1:50'
    assert not sut.parse_non_calculated_hours('Hours: ? {16:00x16:20 + 19:00-20:30}\n')
    log.check(
        ('root', 'DEBUG', "Found: ['16:00-16:20 ', ' 19:00-20:30']"),
        ('root', 'DEBUG', '\tStart: 16:00\tEnd: 16:20\tDelta: 0:20:00'),
        ('root', 'DEBUG', '\tStart: 19:00\tEnd: 20:30\tDelta: 1:30:00'),
        ('root', 'DEBUG', "Found: ['16:00-16:20 ', ' 19:00-20:30']"),
        ('root', 'DEBUG', '\tStart: 16:00\tEnd: 16:20\tDelta: 0:20:00'),
        ('root', 'DEBUG', '\tStart: 19:00\tEnd: 20:30\tDelta: 1:30:00')
    )


def test_parse_calculated_hours(sut, log):
    assert sut.parse_calculated_hours('Hours: 1:50:00 [1.83 h] {16:00-16:20 + 19:00-20:30}\n') == 1.83
    assert sut.parse_calculated_hours('Hours: 1:50:00 [1.83 h] {16:00-16:20 + 19:00-20:30}\n') != 1.833
    log.check(
        ('root', 'INFO', 'There were already 1.83 hours'),
        ('root', 'INFO', 'There were already 1.83 hours')
    )
