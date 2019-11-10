from assertpy import assert_that

from CountHours import read_current_month, read_non_calculated_hours, read_calculated_hours


def test_read_current_month():
    assert_that(read_current_month('## Date: 2013-08-10\n')).is_equal_to('2013-08')
    assert_that(read_current_month('## Date: 2013-08-10\n')).is_not_equal_to('2013-08-10')


def test_read_non_calculated_hours():
    assert_that(str(read_non_calculated_hours('Hours: ? (16:00-16:20 + 19:00-20:30)\n'))).is_equal_to('1:50:00')
    assert_that(str(read_non_calculated_hours('Hours: ? (16:00-16:20 + 19:00-20:30)\n'))).is_not_equal_to('1:50')


def test_read_calculated_hours():
    assert_that(read_calculated_hours('Hours: 1:50:00 [1.83 h] (16:00-16:20 + 19:00-20:30)\n')).is_equal_to(1.83)
    assert_that(read_calculated_hours('Hours: 1:50:00 [1.83 h] (16:00-16:20 + 19:00-20:30)\n')).is_not_equal_to(1.833)
