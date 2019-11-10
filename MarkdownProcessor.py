import logging
import re
import sys
from datetime import datetime


class MarkdownProcessor:
    _modified_lines = 0
    _parse_current_month_re = re.compile(r'([0-9]{4}-[0-9]{2})')
    _parse_non_calculated_hours_segments_re = re.compile(r'[(]([-+: 0-9]*)[)]')
    _parse_non_calculated_hours_segment_re = re.compile(r'([0-2][0-9]:[0-5][0-9])-([0-2][0-9]:[0-5][0-9])')
    _parse_calculated_hours_re = re.compile(r'\[([.0-9]*)[ h\]]')

    def parse_current_month(self, line):
        result = self._parse_current_month_re.search(line)
        return result.group(1)

    def parse_non_calculated_hours(self, line):
        _total_time = None

        result = self._parse_non_calculated_hours_segments_re.search(line)
        if not result:
            return None

        else:
            segments = result.group(1).split('+')
            logging.debug('Found: %s', segments)
            for segment in segments:
                result = self._parse_non_calculated_hours_segment_re.search(segment)
                if not result:
                    return None

                start = result.group(1)
                end = result.group(2)
                delta_time = datetime.strptime(end, '%H:%M') - datetime.strptime(start, '%H:%M')
                logging.debug('\tStart: %s\tEnd: %s\tDifference: %s', start, end, delta_time)
                if _total_time:
                    _total_time = _total_time + delta_time
                else:
                    _total_time = delta_time

        return _total_time

    def parse_calculated_hours(self, line):
        result = self._parse_calculated_hours_re.search(line)
        if not result:
            return None

        else:
            f = float(result.group(1))
            logging.debug('Found: %f', f)
            return f

    def process(self, lines: list) -> list:
        logging.debug('Processing %d lines', len(lines))
        self._modified_lines = 0

        months = {}
        current_month = None
        summary_line_index = len(lines)
        for i, line in enumerate(lines):
            if line.startswith('# Summary'):
                summary_line_index = i
                break

            elif line.startswith('## Date: '):
                # Llegeix el mes
                current_month = self.parse_current_month(line)

            elif line.startswith('Hours: ?'):
                # Llegeix ses hores sense calcular
                total_time = self.parse_non_calculated_hours(line)
                if not total_time:
                    sys.exit('Error in line format "{0}"'.format(line))

                # Convertim el temps a format decimal
                hexa_time = str(total_time)
                splitted_time = hexa_time.split(':')
                decimal_time = int(splitted_time[0]) + (int(splitted_time[1]) / 60)
                formatted_time = '{0} [{1:0.2f} h]'.format(hexa_time, decimal_time)
                logging.info('Added {0:0.2f} Hours'.format(decimal_time))

                # Actualitza ses hores del mes en curs
                months[current_month] = months.get(current_month, 0) + decimal_time

                # Substitueix el simbol ? per el temps calculat
                self._modified_lines += 1
                lines[i] = line.replace('?', formatted_time)

            elif line.startswith('Hours: '):
                # Llegeix ses hores ja calculades per al resum
                decimal_time = self.parse_calculated_hours(line)

                if decimal_time is None:
                    sys.exit('Error in line format "{0}"'.format(line))
                else:
                    logging.info("There were already {0:0.2f} hours".format(decimal_time))

                    # Actualitza ses hores del mes en curs
                    months[current_month] = months.get(current_month, 0) + decimal_time

        # Escriu el resumen
        lines = lines[: summary_line_index]
        lines.append('# Summary:\n')
        for month in months:
            msg = '{0} = {1:0.2f} h'.format(month, months.get(month, 0))
            logging.info(msg)
            lines.append('- {0}\n'.format(msg))

        return lines

    def has_changed(self) -> bool:
        logging.debug('There are %d modified lines', self._modified_lines)
        return self._modified_lines > 0
