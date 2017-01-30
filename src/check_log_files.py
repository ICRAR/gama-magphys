#! /usr/bin/env python
#
#    (c) UWA, The University of Western Australia
#    M468/35 Stirling Hwy
#    Perth WA 6009
#    Australia
#
#    Copyright by UWA, 2012-2015
#    All rights reserved
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston,
#    MA 02111-1307  USA
#
"""
Check the log files after a slurm run
"""
import argparse
import glob
import os

import logging

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)-15s:' + logging.BASIC_FORMAT)


class LogFile:
    def __init__(self, full_path_name):
        self._full_path_name = full_path_name
        self._file_name = None

    def __str__(self):
        return self._full_path_name

    def __lt__(self, other):
        return self._full_path_name.__lt__(other.full_path_name)

    def correct_name(self):
        if os.path.isfile(self._full_path_name):
            (ignored_head, self._file_name) = os.path.split(self._full_path_name)
            (base_name, extension) = os.path.splitext(self._file_name)

            return base_name.isdigit()

        return False

    @property
    def file_name(self):
        return self._file_name

    @property
    def full_path_name(self):
        return self._full_path_name


class SlurmOutput:
    def __init__(self, file_name):
        self._file_name = file_name

    def __str__(self):
        return self._file_name

    def __lt__(self, other):
        return self._file_name.__lt__(other.file_name)

    def correct_name(self):
        if os.path.isfile(self._file_name):
            (ignored_head, file_name) = os.path.split(self._file_name)
            (base_name, extension) = os.path.splitext(file_name)

            elements = base_name[6:].split('_')

            return len(elements) == 2 and elements[0].isdigit() and elements[1].isdigit()

        return False

    @property
    def file_name(self):
        return self._file_name


class OutputDirectory:
    def __init__(self, directory_name):
        self._directory_name = directory_name
        self._directory_number = None

    def __str__(self):
        return self._directory_name

    def __lt__(self, other):
        return self._directory_name.__lt__(other.directory_name)

    def correct_name(self):
        if os.path.isdir(self._directory_name):
            (ignored_head, directory_name) = os.path.split(self._directory_name)
            (self._directory_number, extension) = os.path.splitext(directory_name)

            return self._directory_number.isdigit() and extension == ''

        return False

    @property
    def directory_number(self):
        return self._directory_number

    @property
    def directory_name(self):
        return self._directory_name


class ProcessLogs:
    def __init__(self, log_directory_name, output_directory_name):
        self._log_directory_name = log_directory_name
        self._output_directory_name = output_directory_name
        self._errors = []

    @staticmethod
    def _check_exists(directory_name):
        if not os.path.exists(directory_name):
            LOG.error('The directory {0} does not exists'.format(directory_name))
            return False

        if not os.path.isdir(directory_name):
            LOG.error('{0} is not a directory'.format(directory_name))
            return False

        return True

    def check_exists(self):
        check_log = self._check_exists(self._log_directory_name)
        check_output = self._check_exists(self._output_directory_name)

        return check_log and check_output

    def process(self):
        # Get the names of the log files etc
        log_files = []
        for file_name in glob.glob(os.path.join(self._log_directory_name, '*.log')):
            log_file = LogFile(file_name)
            if log_file.correct_name():
                log_files.append(log_file)
        log_files = sorted(log_files)

        slurm_files = []
        for file_name in glob.glob(os.path.join(self._log_directory_name, 'slurm-*.out')):
            output = SlurmOutput(file_name)
            if output.correct_name():
                slurm_files.append(output)
        slurm_files = sorted(slurm_files)

        output_directories = []
        for directory_name in os.listdir(self._output_directory_name):
            directory = OutputDirectory(os.path.join(self._output_directory_name, directory_name))
            if directory.correct_name():
                output_directories.append(directory)
        output_directories = sorted(output_directories)

        # Make sure we have the right number of files
        self._check01(log_files, slurm_files, output_directories)

        # Make sure the log files end correctly
        self._check02(log_files)

        # Make sure the slurm files are correct
        self._check03(slurm_files)

        for error in self._errors:
            LOG.error(error)

    def _check01(self, log_files, slurm_files, output_directories):
        LOG.info('Check 01')
        if len(log_files) != len(output_directories):
            self._errors.append('The number of log files does not match the number of output directories. '
                                'Log files: {0} Output directories {1}'.format(len(log_files), len(output_directories)))

        expected_log_files = set([output_directory.directory_number + '.log' for output_directory in output_directories])
        for log_file in log_files:
            if log_file.file_name in expected_log_files:
                expected_log_files.remove(log_file.file_name)
            else:
                self._errors.append('We are missing the log file {0}'.format(log_file))

        for expected_log_file in sorted(expected_log_files):
            self._errors.append('The log file {0} was not generated'.format(expected_log_file))

        number_slurm_files = len(output_directories) / 24 + 1
        if number_slurm_files != len(slurm_files):
            self._errors.append('The number of slurm files does not match the number of output directories. '
                                'Slurm files: {0} Output directories {1} expected: {2}'.format(len(slurm_files), len(output_directories), number_slurm_files))

    def _check02(self, log_files):
        LOG.info('Check 02')

        for log_file in log_files:
            with open(log_file.full_path_name, 'r') as read_file:
                data = read_file.readlines()

                if len(data) <= 10:
                    self._errors.append('The file {0} appears to be too short'.format(log_file))

                count_total_wall_time = 0
                for line in data:
                    if line.startswith('Total wall time'):
                        count_total_wall_time += 1

                if count_total_wall_time != 2:
                    self._errors.append('The run logged in {0} does not appear to have finished correctly'.format(log_file))

    def _check03(self, slurm_files):
        LOG.info('Check 03')

        for slurm_file in slurm_files:
            with open(slurm_file.file_name, 'r') as read_file:
                data = read_file.readlines()

                if len(data) <= 10:
                    self._errors.append('The file {0} appears to be too short'.format(slurm_file))

                count_completed = 0
                for line in data:
                    if line.startswith('Completed directory = '):
                        count_completed += 1

                if count_completed != 24:
                    self._errors.append('The run logged in {0} does not appear to have finished correctly. '
                                        'There are only {1} "Completed directories".'.format(slurm_file, count_completed))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('log_directory_name', nargs=1, help='the directory with the log files')
    parser.add_argument('output_directory_name', nargs=1, help='the directory with the output files')
    args = parser.parse_args()

    process_logs = ProcessLogs(args.log_directory_name[0], args.output_directory_name[0])
    if process_logs.check_exists():
        process_logs.process()

if __name__ == "__main__":
    main()
