import logging
import re
from datetime import datetime


class MarkdownProcessor:
    _modified_lines = 0
    _parse_current_month_re = re.compile(r'([0-9]{4}-[0-9]{2})')
    _parse_non_calculated_hours_segments_re = re.compile(r'[(]([-+: 0-9]*)[)]')
    _parse_non_calculated_hours_segment_re = re.compile(r'([0-2][0-9]:[0-5][0-9])-([0-2][0-9]:[0-5][0-9])')
    _parse_calculated_hours_re = re.compile(r'\[([.0-9]*)[ h\]]')

    def process(self, lines: list) -> list:
        logging.debug('Processing %d lines', len(lines))
        self._modified_lines = 0

        months = {}
        current_month = None
        summary_line_index = len(lines)
        for i, line in enumerate(lines):
            if self._is_summary(line):
                summary_line_index = i
                break

            elif self._is_date(line):
                current_month = self.parse_current_month(line)

            elif self._are_non_calculated_hours(line):
                (str_time, decimal_time) = self._get_time(line)
                lines[i] = line.replace('?', self._format_time(str_time, decimal_time))
                months[current_month] = months.get(current_month, 0) + decimal_time
                self._modified_lines += 1

            elif self._are_calculated_hours(line):
                decimal_time = self.parse_calculated_hours(line)
                months[current_month] = months.get(current_month, 0) + decimal_time

        lines = lines[: summary_line_index]
        lines = lines + self._summary_lines(months)
        return lines

    @staticmethod
    def _is_date(line: str) -> bool:
        return line.startswith('## Date: ')

    @staticmethod
    def _is_summary(line: str) -> bool:
        return line.startswith('# Summary')

    def parse_current_month(self, line):
        result = self._parse_current_month_re.search(line)
        return result.group(1)

    @staticmethod
    def _are_non_calculated_hours(line: str) -> bool:
        return line.startswith('Hours: ?')

    def _get_time(self, line: str):
        total_time = self.parse_non_calculated_hours(line)
        if not total_time:
            raise Exception('Error in line format "{0}"'.format(line))

        str_time = str(total_time)
        time_parts = str_time.split(':')
        decimal_time = int(time_parts[0]) + (int(time_parts[1]) / 60)
        logging.info('Added {0:0.2f} Hours'.format(decimal_time))
        return str_time, decimal_time

    def parse_non_calculated_hours(self, line):
        _total_time = None
        result = self._parse_non_calculated_hours_segments_re.search(line)
        if not result:
            return None

        else:
            segments = result.group(1).split('+')
            logging.debug('Found: %s', segments)
            for segment in segments:
                delta_time = self._calculate_delta_time(segment)
                if _total_time:
                    _total_time = _total_time + delta_time
                else:
                    _total_time = delta_time

        return _total_time

    def _calculate_delta_time(self, segment):
        result = self._parse_non_calculated_hours_segment_re.search(segment)
        if not result:
            return None

        start = result.group(1)
        end = result.group(2)
        delta_time = datetime.strptime(end, '%H:%M') - datetime.strptime(start, '%H:%M')
        logging.debug('\tStart: %s\tEnd: %s\tDelta: %s', start, end, delta_time)
        return delta_time

    @staticmethod
    def _format_time(str_time, decimal_time) -> str:
        return '{0} [{1:0.2f} h]'.format(str_time, decimal_time)

    @staticmethod
    def _are_calculated_hours(line: str) -> bool:
        return line.startswith('Hours: ')

    def parse_calculated_hours(self, line) -> float:
        result = self._parse_calculated_hours_re.search(line)
        if not result:
            raise Exception('Error in line format "{0}"'.format(line))
        decimal_time = float(result.group(1))
        logging.info("There were already {0:0.2f} hours".format(decimal_time))
        return decimal_time

    @staticmethod
    def _summary_lines(months):
        new_lines = ['# Summary:\n']
        for month in months:
            msg = '{0} = {1:0.2f} h'.format(month, months.get(month, 0))
            new_lines.append('- {0}\n'.format(msg))
            logging.info(msg)
        return new_lines

    def has_changed(self) -> bool:
        logging.debug('There are %d modified lines', self._modified_lines)
        return self._modified_lines > 0
