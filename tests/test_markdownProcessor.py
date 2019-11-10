import logging

import pytest
from assertpy import assert_that
from testfixtures import LogCapture

from MarkdownProcessor import MarkdownProcessor


def teardown_module(module):
    LogCapture.uninstall_all()


@pytest.fixture()
def log():
    return LogCapture(level=logging.DEBUG)


@pytest.fixture()
def sut():
    return MarkdownProcessor()


def test_process_without_changes(sut):
    lines = [
        '# To do:\n',
        '- Some pending tasks\n',
        '# Actions:\n',
        '## Date: 2014-01-17\n',
        'Hours: 0:38:00 [0.63 h] (16:18-16:38 + 16:41-16:59 - 19:00-19:20)\n',
        '- Watermark with logo\n',
        '- Credits\n',
        '# Summary:\n',
        '- 2014-01 = 0.63 h\n'
    ]
    actual = sut.process(lines)
    has_changed = sut.has_changed()

    assert_that(actual).is_equal_to(lines)
    assert_that(has_changed).is_false()


def test_process_with_changes(sut):
    lines = [
        '# To do:\n',
        '- Some pending tasks\n',
        '# Actions:\n',
        '## Date: 2014-02-10\n',
        'Hours: ? (18:43-18:46 + 21:41-22:25)\n',
        '- Check and tag\n',
        '- Export and upload\n',
        '## Date: 2014-01-20\n',
        'Hours: ? (17:10-19:30)\n',
        '- Editing video\n',
        '- Sound normalization\n',
        '- Color grading\n',
        '## Date: 2014-01-17\n',
        'Hours: 0:38:00 [0.63 h] (16:18-16:38 + 16:41-16:59 - 19:00-19:20)\n',
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
        'Hours: 0:47:00 [0.78 h] (18:43-18:46 + 21:41-22:25)\n',
        '- Check and tag\n',
        '- Export and upload\n',
        '## Date: 2014-01-20\n',
        'Hours: 2:20:00 [2.33 h] (17:10-19:30)\n',
        '- Editing video\n',
        '- Sound normalization\n',
        '- Color grading\n',
        '## Date: 2014-01-17\n',
        'Hours: 0:38:00 [0.63 h] (16:18-16:38 + 16:41-16:59 - 19:00-19:20)\n',
        '- Watermark with logo\n',
        '- Credits\n',
        '# Summary:\n',
        '- 2014-02 = 0.78 h\n',
        '- 2014-01 = 2.96 h\n'
    ]
    assert_that(actual).is_equal_to(expected)
    assert_that(has_changed).is_true()


def test_parse_current_month(sut):
    assert_that(sut.parse_current_month('## Date: 2013-08-10\n')).is_equal_to('2013-08')
    assert_that(sut.parse_current_month('## Date: 2013-08-10\n')).is_not_equal_to('2013-08-10')


def test_parse_non_calculated_hours(sut):
    assert_that(str(sut.parse_non_calculated_hours('Hours: ? (16:00-16:20 + 19:00-20:30)\n'))).is_equal_to('1:50:00')
    assert_that(str(sut.parse_non_calculated_hours('Hours: ? (16:00-16:20 + 19:00-20:30)\n'))).is_not_equal_to('1:50')


def test_parse_calculated_hours(sut):
    assert_that(sut.parse_calculated_hours('Hours: 1:50:00 [1.83 h] (16:00-16:20 + 19:00-20:30)\n')).is_equal_to(1.83)
    assert_that(sut.parse_calculated_hours('Hours: 1:50:00 [1.83 h] (16:00-16:20 + 19:00-20:30)\n')).is_not_equal_to(1.833)
