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
echo way_fit,$DIFF,{2} >> timings.csv

START=$(date +%s)
if [ ! -f {1}.sed ]; then
  echo "processing {0} - {1}"
  echo {0} | $magphys/fit_sed_highz
else
  echo "skipping {0} - {1}"
fi
END=$(date +%s)
DIFF=$(echo "$END - $START" | bc)
echo Fit took $DIFF seconds
echo fit,$DIFF,{3} >> timings.csv
'''

CLOSE_FILE = '''
END=$(date +%s)
DIFF=$(echo "$END - $OVERALL_START" | bc)
echo '------------'
echo Total wall time actual $DIFF seconds
echo Total wall time expected {0} seconds
echo '------------'
echo total,$DIFF,{0} >> timings.csv

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
echo Wall time expected {1} seconds
echo '----'
echo way_get_optic_colors_highz,$DIFF,{1} >> timings.csv

# Create the models
echo "{0}
70.0,0.3,0.7" > redshift

echo N | $magphys/make_zgrid

START=$(date +%s)

cat redshift | $magphys/get_optic_colors_highz

END=$(date +%s)
DIFF=$(echo "$END - $START" | bc)
echo get_optic_colors_highz took $DIFF seconds
echo get_optic_colors_highz,$DIFF,{3} >> timings.csv

# Timing information
NOW=$(date +%s)
DIFF=$(echo "$NOW - $OVERALL_START" | bc)
echo '----'
echo Wall time actual $DIFF seconds
echo Wall time expected {2} seconds
echo '----'
echo way_get_infrared_colors_highz,$DIFF,{2} >> timings.csv

START=$(date +%s)

cat redshift | $magphys/get_infrared_colors_highz

END=$(date +%s)
DIFF=$(echo "$END - $START" | bc)
echo get_infrared_colors_highz took $DIFF seconds
echo get_infrared_colors_highz,$DIFF,{4} >> timings.csv

'''

HEADER = '''#!/bin/bash
# Use MagPhys to process one pixel
#
OVERALL_START=$(date +%s)
echo task,actual,expected > timings.csv

export magphys={1}
export scratch={0}
cd $scratch

export FILTERS={1}/FILTERBIN.RES
export OPTILIB=$magphys/OptiLIB_bc03_highz.bin
export OPTILIBIS=$magphys/OptiLIBis_bc03_highz.bin
export IRLIB=$magphys/InfraredLIB_highz.bin
export USER_FILTERS={2}
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
        self._csv_file_name = kwargs['csv_file_name']
        self._dir_out_root_name = kwargs['dir_out_root_name']
        self._dir_magphys = kwargs['dir_magphys']
        self._filters_dat = kwargs['filters_dat']
        self._time_infrared_colors = kwargs['time_infrared_colors']
        self._time_optical_colors = kwargs['time_optical_colors']
        self._time_fit = kwargs['time_fit']
        self._wall_time = kwargs['wall_time'] - int(kwargs['wall_time'] * 0.05)  # Take off 5%
        self._separator = kwargs['separator']
        self._has_header_row = kwargs['has_header_row']

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
            output_file.write('echo "{0} {1} {2}" >> mygals.dat\n'.format(galaxy.galaxy_id, galaxy.redshift, galaxy.filter_values))

    def check_exists(self):
        if not os.path.exists(self._csv_file_name):
            LOG.error('The file {0} does not exist'.format(self._csv_file_name))
            return False

        if not os.path.isdir(self._dir_out_root_name):
            LOG.error('The directory {0} does not exist'.format(self._dir_out_root_name))
            return False

        return True

    def _get_galaxies_by_red_shift(self):
        LOG.info('Reading {0}'.format(self._csv_file_name))
        galaxies_by_red_shift = {}
        _0001 = Decimal('.0001')
        _0 = Decimal('0.0')
        _6 = Decimal('6.0')

        with open(self._csv_file_name, 'r') as dat_file:
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
        return galaxies_by_red_shift

    def _open_outputfile(self, directory_counter):
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

    def _write_out_galaxies(self, galaxies_by_red_shift):
        directory_counter = 0
        output_file = None
        accumulated_wall_time = 0
        LOG.info('{0} entries to process'.format(len(galaxies_by_red_shift.keys())))

        for redshift in galaxies_by_red_shift.keys():
            redshift_group = galaxies_by_red_shift[redshift]

            # Partition the list
            partitioned_list = self._partition_list(redshift_group.list_of_galaxies, accumulated_wall_time)

            index = 0
            for list_of_galaxies in partitioned_list:
                # Update the index
                index += 1

                # Do we need to close the file down?
                if len(list_of_galaxies) == 0 and output_file is not None:
                    self._close_file(output_file, accumulated_wall_time)
                    output_file = None
                    continue

                if output_file is None:
                    output_file, directory_name = self._open_outputfile(directory_counter)
                    output_file.write(
                        HEADER.format(
                            directory_name,
                            self._dir_magphys,
                            self._filters_dat
                        )
                    )
                    directory_counter += 1
                    accumulated_wall_time = 0

                # Log what we are adding
                LOG.info('Adding redshift:{0} galaxies:{1}'.format(redshift, len(list_of_galaxies)))

                # Check if we need to build models
                self._write_check_we_have_something_to_do(output_file, list_of_galaxies)

                self._write_data_file(output_file, list_of_galaxies)
                output_file.write(
                    MODEL_GENERATION.format(
                        redshift,
                        accumulated_wall_time,
                        accumulated_wall_time + self._time_optical_colors,
                        self._time_optical_colors,
                        self._time_infrared_colors
                    )
                )
                accumulated_wall_time += self._time_infrared_colors + self._time_optical_colors
                galaxy_id = 1
                for galaxy in list_of_galaxies:
                    output_file.write(RUN_MAGPHYS.format(galaxy_id, galaxy.galaxy_id, accumulated_wall_time, self._time_fit))
                    galaxy_id += 1
                    accumulated_wall_time += self._time_fit

                output_file.write(FI)
                output_file.write(RM_LBR)

                # Make sure we don't close the last one
                if index < len(partitioned_list):
                    self._close_file(output_file, accumulated_wall_time)
                    output_file = None

        # Close the last file
        if output_file is not None:
            self._close_file(output_file, accumulated_wall_time)

    def process_file(self):
        galaxies_by_red_shift = self._get_galaxies_by_red_shift()

        self._write_out_galaxies(galaxies_by_red_shift)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('csv_file_name', nargs=1, help='the csv file to use')
    parser.add_argument('dir_out_root_name', nargs=1, help='where the files are to be written')
    parser.add_argument('magphys', nargs=1, help='where the magphys executable files are to be found')
    parser.add_argument('filters_dat', nargs=1, help='where the filters.dat file is to be found')

    parser.add_argument('--time_infrared_colors', type=int, help='the time (in seconds) for get_infrared_colors to run', default=1 * 60)
    parser.add_argument('--time_optical_colors', type=int, help='the time (in seconds) for get_optical_colors to run', default=1 * 60)
    parser.add_argument('--time_fit', type=int, help='the time (in seconds) to perform a fit', default=1 * 60)
    parser.add_argument('--wall_time', type=int, help='the wall time (in seconds)', default=180 * 60)
    parser.add_argument('--has_header_row', action='store_true', help='does the input file have a header row', default=False)
    parser.add_argument('--separator', help='what separator does the file use', default=',')
    args = parser.parse_args()

    preprocess = Preprocess(
        csv_file_name=args.csv_file_name[0],
        dir_out_root_name=args.dir_out_root_name[0],
        dir_magphys=args.magphys[0],
        filters_dat=args.filters_dat[0],
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
