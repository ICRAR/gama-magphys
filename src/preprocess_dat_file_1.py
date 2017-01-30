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
Preprocess the dat file
"""
import argparse
import os

import logging
from decimal import Decimal

RUN_MAGPHYS = '''
# Timing information
NOW=$(date +%s)
DIFF=$(echo "$NOW - $OVERALL_START" | bc)
echo '----'
echo Wall time actual $DIFF seconds
echo Wall time expected {2} seconds
echo '----'
echo way_fit,$DIFF,{2},{4} >> timings.csv

START=$(date +%s)
if [ ! -f {1}.sed ]; then
  echo "processing {0} - {1}"
  echo {0} | $magphys/fit_sed_zz2_uplimits
else
  echo "skipping {0} - {1}"
fi
END=$(date +%s)
DIFF=$(echo "$END - $START" | bc)
echo Fit took $DIFF seconds
echo fit,$DIFF,{3},{4} >> timings.csv
'''

CLOSE_FILE = '''
END=$(date +%s)
DIFF=$(echo "$END - $OVERALL_START" | bc)
echo '------------'
echo Total wall time actual $DIFF seconds
echo Total wall time expected {0} seconds
echo '------------'
echo total,$DIFF,{0},NaN >> timings.csv

'''

RM_LBR = '''

# Remove any models
/bin/rm -f *.lbr

'''

THEN = '''; then

'''

CHECK_WE_HAVE_SOMETHING_TO_DO = '''# Check we have something to do
if '''

FI = '''
fi
'''

MODEL_GENERATION = '''
# Timing information
NOW=$(date +%s)
DIFF=$(echo "$NOW - $OVERALL_START" | bc)
echo '----'
echo Wall time actual $DIFF seconds
echo Wall time expected {2} seconds
echo '----'
echo way_get_optic_colors,$DIFF,{2},{0} >> timings.csv

# Create the models
echo "{0}
70.0,0.3,0.7" > redshift

echo N | $magphys/make_zgrid

START=$(date +%s)

cat redshift | $magphys/get_optic_colors

END=$(date +%s)
DIFF=$(echo "$END - $START" | bc)
echo get_optic_colors took $DIFF seconds
echo get_optic_colors,$DIFF,{4},{0} >> timings.csv

# Timing information
NOW=$(date +%s)
DIFF=$(echo "$NOW - $OVERALL_START" | bc)
echo '----'
echo Wall time actual $DIFF seconds
echo Wall time expected {3} seconds
echo '----'
echo way_{1},$DIFF,{3},{0} >> timings.csv

START=$(date +%s)

cat redshift | $magphys/{1}

END=$(date +%s)
DIFF=$(echo "$END - $START" | bc)
echo {1} took $DIFF seconds
echo {1},$DIFF,{5},{0} >> timings.csv

'''

HEADER = '''#!/bin/bash
# Use MagPhys to process one pixel
#
OVERALL_START=$(date +%s)
echo task,actual,expected,redshift > timings.csv

export magphys={1}/magphys
export scratch={0}
cd $scratch

export FILTERS={1}/runs/{2}/FILTERBIN.RES
export OPTILIB=$magphys/OptiLIB_{3}.bin
export OPTILIBIS=$magphys/OptiLIBis_{3}.bin
export IRLIB=$magphys/InfraredLIB.bin
export USER_FILTERS={1}/runs/{2}/filters.dat
export USER_OBS=$scratch/mygals.dat

/bin/rm -f *.lbr

'''

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)-15s:' + logging.BASIC_FORMAT)


class Galaxy:
    def __init__(self, galaxy_id, redshift, filter_values):
        self._galaxy_id = galaxy_id
        self._redshift = redshift
        self._filter_values = filter_values

    @property
    def galaxy_id(self):
        return self._galaxy_id

    @property
    def redshift(self):
        return self._redshift

    @property
    def filter_values(self):
        return self._filter_values


class RedshiftGroup:
    def __init__(self, redshift, list_of_galaxies):
        self._redshift = redshift
        self._list_of_galaxies = list_of_galaxies

    @property
    def redshift(self):
        return self._redshift

    @property
    def list_of_galaxies(self):
        return self._list_of_galaxies


class Preprocess:
    def __init__(self, **kwargs):
        self._dat_file_name = kwargs['dat_file_name']
        self._dir_out_root_name = kwargs['dir_out_root_name']
        self._dir_magphys = kwargs['dir_magphys']
        self._run = kwargs['run']
        self._magphys_library = kwargs['magphys_library']
        self._get_infrared_colors = kwargs['get_infrared_colors']
        self._time_infrared_colors = kwargs['time_infrared_colors']
        self._time_optical_colors = kwargs['time_optical_colors']
        self._time_fit = kwargs['time_fit']
        self._wall_time = kwargs['wall_time'] - int(kwargs['wall_time'] * 0.05)  # Take off 5%
        self._separator = kwargs['separator']
        self._has_header_row = kwargs['has_header_row']
        self._redshift_group_by_length = {}

    @staticmethod
    def _write_check_we_have_something_to_do(output_file, galaxies):
        output_file.write(CHECK_WE_HAVE_SOMETHING_TO_DO)
        add_or = False
        for galaxy in galaxies:
            if add_or:
                output_file.write(' || ')
            output_file.write('[ ! -f {0}.sed ]'.format(galaxy.galaxy_id))
            add_or = True

        output_file.write(THEN)

    @staticmethod
    def _close_file(output_file, accumulated_wall_time):
        output_file.write(CLOSE_FILE.format(accumulated_wall_time))
        output_file.close()

    @staticmethod
    def _write_data_file(output_file, galaxies):
        output_file.write('''
# Next galaxies
echo "# Header" > mygals.dat
''')
        for galaxy in galaxies:
            # Need the 4 digit redshift
            output_file.write('echo "{0} {1} {2}" >> mygals.dat'.format(galaxy.galaxy_id, galaxy.redshift, galaxy.filter_values))

    def check_exists(self):
        if not os.path.exists(self._dat_file_name):
            LOG.error('The file {0} does not exist'.format(self._dat_file_name))
            return False

        if not os.path.isdir(self._dir_out_root_name):
            LOG.error('The directory {0} does not exist'.format(self._dir_out_root_name))
            return False

        return True

    def _get_galaxies_by_red_shift(self):
        LOG.info('Reading {0}'.format(self._dat_file_name))
        galaxies_by_red_shift = {}
        _0001 = Decimal('.0001')
        _0 = Decimal('0.0')
        _6 = Decimal('6.0')

        with open(self._dat_file_name, 'r') as dat_file:
            line_number = 1
            for line in dat_file:
                if line_number == 1 and self._has_header_row:
                    line_number = 2
                    continue

                # remove whitespace
                line = line.strip()

                # Parse the line to remove bogus redshifts
                elements = line.split(self._separator)

                # noinspection PyBroadException
                try:
                    # Red shift must be positive
                    redshift = Decimal(elements[1]).quantize(_0001)
                    if _0 < redshift <= _6:
                        redshift = str(redshift)
                        redshift_group = galaxies_by_red_shift.get(redshift)
                        if redshift_group is None:
                            redshift_group = RedshiftGroup(redshift, [])
                            galaxies_by_red_shift[redshift] = redshift_group

                        redshift_group.list_of_galaxies.append(
                            Galaxy(
                                elements[0],
                                redshift,
                                ' '.join(elements[2:])))
                except Exception:
                    LOG.exception('Error processing line {0} - {1}'.format(line_number, line))

                line_number += 1

        # Convert to a map based on length
        for redshift_group in galaxies_by_red_shift.values():
            length = len(redshift_group.list_of_galaxies)
            elements = self._redshift_group_by_length.get(length)
            if elements is None:
                elements = []
                self._redshift_group_by_length[length] = elements
            elements.append(redshift_group)

    def _open_output_file(self, directory_counter):
        directory_name = os.path.join(self._dir_out_root_name, '{0:06d}'.format(directory_counter))
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)

        file_name = os.path.join(directory_name, 'process_data.sh')
        LOG.info('Creating {0}'.format(file_name))
        output_file = open(file_name, 'w')
        return output_file, directory_name

    def _partition_list(self, galaxy_list, accumulated_wall_time):
        partitioned_list = []
        sub_list = []

        if len(galaxy_list) * self._time_fit + self._time_infrared_colors + self._time_optical_colors + accumulated_wall_time < self._wall_time:
            # It'll all fit
            sub_list.extend(galaxy_list)
        else:
            if self._time_fit + self._time_infrared_colors + self._time_optical_colors + accumulated_wall_time > self._wall_time:
                # We can't even fit 1 so start a new file
                partitioned_list.append([])
                accumulated_wall_time = 0

            accumulated_wall_time += self._time_infrared_colors + self._time_optical_colors
            for galaxy in galaxy_list:
                if accumulated_wall_time + self._time_fit > self._wall_time:
                    partitioned_list.append(sub_list)
                    sub_list = []
                    accumulated_wall_time = self._time_infrared_colors + self._time_optical_colors
                sub_list.append(galaxy)
                accumulated_wall_time += self._time_fit

        partitioned_list.append(sub_list)
        return partitioned_list

    def _get_redshift_group(self, accumulated_wall_time):
        time_left = self._wall_time - accumulated_wall_time - self._time_infrared_colors - self._time_optical_colors
        items = time_left / self._time_fit

        if accumulated_wall_time == 0:
            # Get the biggest list
            max_length = self._get_biggest_list()

            if max_length is not None:
                return self.get_slice_of_galaxies(max_length, items)
            else:
                return None
        else:
            if items in self._redshift_group_by_length:
                return self.get_slice_of_galaxies(items, items)
            else:
                max_length = self._get_biggest_list()
                if max_length is not None:
                    return self.get_slice_of_galaxies(max_length, items)
                else:
                    return None

    def get_slice_of_galaxies(self, length_key, items):
        list_redshift_group = self._redshift_group_by_length.get(length_key)
        if len(list_redshift_group) == 1:
            # Last one
            self._redshift_group_by_length.pop(length_key)

        redshift_group = list_redshift_group.pop()
        if len(redshift_group.list_of_galaxies) <= items:
            return redshift_group
        else:
            new_list = []
            for i in range(0, items):
                new_list.append(redshift_group.list_of_galaxies.pop())

            length_key = len(redshift_group.list_of_galaxies)
            elements = self._redshift_group_by_length.get(length_key)
            if elements is None:
                elements = []
                self._redshift_group_by_length[length_key] = elements
            elements.append(redshift_group)

            return RedshiftGroup(redshift_group.redshift, new_list)

    def _get_biggest_list(self):
        max_length = None
        for length in self._redshift_group_by_length.keys():
            if max_length is None:
                max_length = length
            elif length > max_length:
                max_length = length
        return max_length

    def _write_out_galaxies(self):
        directory_counter = 0
        output_file = None
        accumulated_wall_time = 0

        while len(self._redshift_group_by_length) > 0:
            redshift_group = self._get_redshift_group(accumulated_wall_time)

            if output_file is None:
                output_file, directory_name = self._open_output_file(directory_counter)
                output_file.write(HEADER.format(directory_name, self._dir_magphys, self._run, self._magphys_library))
                directory_counter += 1

            # Log what we are adding
            LOG.info('Adding redshift:{0} galaxies:{1}'.format(redshift_group.redshift, len(redshift_group.list_of_galaxies)))

            # Check if we need to build models
            self._write_check_we_have_something_to_do(output_file, redshift_group.list_of_galaxies)

            self._write_data_file(output_file, redshift_group.list_of_galaxies)
            output_file.write(MODEL_GENERATION.format(redshift_group.redshift,
                                                      self._get_infrared_colors,
                                                      accumulated_wall_time,
                                                      accumulated_wall_time + self._time_optical_colors,
                                                      self._time_optical_colors,
                                                      self._time_infrared_colors))
            accumulated_wall_time += self._time_infrared_colors + self._time_optical_colors
            galaxy_id = 1
            for galaxy in redshift_group.list_of_galaxies:
                output_file.write(RUN_MAGPHYS.format(galaxy_id, galaxy.galaxy_id, accumulated_wall_time, self._time_fit, redshift_group.redshift))
                galaxy_id += 1
                accumulated_wall_time += self._time_fit

            output_file.write(FI)
            output_file.write(RM_LBR)

            # Make sure we close it if we can't fit any more in
            if self._time_fit + self._time_infrared_colors + self._time_optical_colors + accumulated_wall_time > self._wall_time:
                self._close_file(output_file, accumulated_wall_time)
                output_file = None
                accumulated_wall_time = 0

        # Close the last file
        if output_file is not None:
            self._close_file(output_file, accumulated_wall_time)

    def process_file(self):
        self._get_galaxies_by_red_shift()
        self._write_out_galaxies()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dat_file_name', nargs=1, help='the dat file to use')
    parser.add_argument('dir_out_root_name', nargs=1, help='where the files are written')
    parser.add_argument('magphys', nargs=1, help='where the magphys files are to be found')
    parser.add_argument('run', nargs=1, help='where the filters.dat file is to be found')
    parser.add_argument('magphys_library', nargs=1, help='which MAGPHYS optical library to use', choices=['cb07', 'bc03'])
    parser.add_argument('--get_infrared_colors', help='the get_infrared_colors executable name', default='get_infrared_colors')
    parser.add_argument('--time_infrared_colors', type=int, help='the time (in seconds) for get_infrared_colors to run', default=2 * 60)
    parser.add_argument('--time_optical_colors', type=int, help='the time (in seconds) for get_optical_colors to run', default=2 * 60)
    parser.add_argument('--time_fit', type=int, help='the time (in seconds) to perform a fit', default=5 * 60)
    parser.add_argument('--wall_time', type=int, help='the wall time (in seconds)', default=180 * 60)
    parser.add_argument('--has_header_row', action='store_true', help='does the input file have a header row', default=False)
    parser.add_argument('--separator', help='what separator does the file use', default=',')
    args = parser.parse_args()

    preprocess = Preprocess(
        dat_file_name=args.dat_file_name[0],
        dir_out_root_name=args.dir_out_root_name[0],
        dir_magphys=args.magphys[0],
        run=args.run[0],
        magphys_library=args.magphys_library[0],
        get_infrared_colors=args.get_infrared_colors,
        time_infrared_colors=args.time_infrared_colors,
        time_optical_colors=args.time_optical_colors,
        time_fit=args.time_fit,
        wall_time=args.wall_time,
        has_header_row=args.has_header_row,
        separator=args.separator,
    )
    if preprocess.check_exists():
        preprocess.process_file()


if __name__ == "__main__":
    main()
