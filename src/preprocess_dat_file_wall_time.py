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

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)-15s:' + logging.BASIC_FORMAT)


def write_header(output_file, directory_name, magphys_directory, run, magphys_library):
    """
    Write the header
    """
    output_file.write('''#!/bin/bash
# Use MagPhys to process one pixel
#
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

'''.format(directory_name, magphys_directory, run, magphys_library))


def write_model_generation(output_file, redshift, get_infrared_colors):
    output_file.write('''
# Create the models
echo "{0}
70.0,0.3,0.7" > redshift

echo N | $magphys/make_zgrid

START=$(date +%s)

cat redshift | $magphys/get_optic_colors

END=$(date +%s)
DIFF=$(echo "$END - $START" | bc)
echo $DIFF seconds on get_optic_colors

START=$(date +%s)

cat redshift | $magphys/{1}

END=$(date +%s)
DIFF=$(echo "$END - $START" | bc)
echo $DIFF seconds on {1}

'''.format(redshift, get_infrared_colors))


def write_fi(output_file):
    output_file.write('''
fi
''')


def write_check_we_have_something_to_do(output_file, lines):
    output_file.write('''# Check we have something to do
if ''')
    add_or = False
    for line in lines:
        if add_or:
            output_file.write(' || ')
        output_file.write('[ ! -f {0}.sed ]'.format(line[0]))
        add_or = True

    output_file.write('''; then

''')


def write_rm_lbr(output_file):
    output_file.write('''
# Remove any models
/bin/rm -f *.lbr
''')


def write_run_magphys(output_file, galaxy_id, galaxy_number):
    output_file.write('''
START=$(date +%s)
if [ ! -f {2}.sed ]; then
  echo "processing {0} - {1}"
  echo {0} | $magphys/fit_sed_zz2_uplimits
else
  echo "skipping {0} - {1}"
fi
END=$(date +%s)
DIFF=$(echo "$END - $START" | bc)
echo $DIFF seconds
'''.format(galaxy_id, galaxy_number, galaxy_number))


def write_data_file(output_file, redshift, lines):
    output_file.write('''
# Next galaxies
echo "# Header" > mygals.dat
''')
    for line in lines:
        # Need the 4 digit redshift
        output_file.write('echo "{0} {1}'.format(line[0], redshift))

        for element in line[2:]:
            output_file.write(' {0}'.format(element))
        output_file.write('''" >> mygals.dat
'''.format(line))


def check_exists(dat_file_name, dir_root_name):
    if not os.path.exists(dat_file_name):
        LOG.error('The file {0} does not exist'.format(dat_file_name))
        return False

    if not os.path.isdir(dir_root_name):
        LOG.error('The directory {0} does not exist'.format(dir_root_name))
        return False

    return True


def get_galaxies_by_red_shift(dat_file_name, has_header_row, separator):
    LOG.info('Reading {0}'.format(dat_file_name))
    galaxies_by_red_shift = {}
    _0001 = Decimal('.0001')
    _0 = Decimal('0.0')
    _6 = Decimal('6.0')

    with open(dat_file_name, 'r') as dat_file:
        line_number = 1
        for line in dat_file:
            if line_number == 1 and has_header_row:
                line_number = 2
                continue

            # remove whitespace
            line = line.strip()

            # Parse the line to remove bogus redshifts
            elements = line.split(separator)

            # noinspection PyBroadException
            try:
                # Red shift must be positive
                redshift = Decimal(elements[1]).quantize(_0001)
                if _0 < redshift <= _6:
                    redshift = str(redshift)
                    list_of_galaxies = galaxies_by_red_shift.get(redshift)
                    if list_of_galaxies is None:
                        list_of_galaxies = []
                        galaxies_by_red_shift[redshift] = list_of_galaxies

                    list_of_galaxies.append(elements)
            except Exception:
                LOG.exception('Error processing line {0} - {1}'.format(line_number, line))

            line_number += 1
    return galaxies_by_red_shift


def open_outputfile(dir_out_root_name, directory_counter):
    directory_name = os.path.join(dir_out_root_name, '{0:06d}'.format(directory_counter))
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

    file_name = os.path.join(directory_name, 'process_data.sh')
    LOG.info('Creating {0}'.format(file_name))
    output_file = open(file_name, 'w')
    return output_file, directory_name


def partition_list(galaxy_list, time_infrared_colors, time_optical_colors, time_fit, wall_time, accumulated_wall_time):
    partitioned_list = []
    sub_list = []

    if len(galaxy_list) * time_fit + time_infrared_colors + time_optical_colors + accumulated_wall_time < wall_time:
        # It'll all fit
        sub_list.extend(galaxy_list)
    else:
        if 5 * time_fit + time_infrared_colors + time_optical_colors + accumulated_wall_time > wall_time:
            # We can't even fit 5 so start a new file
            partitioned_list.append(sub_list)
            accumulated_wall_time = 0

        accumulated_wall_time += time_infrared_colors + time_optical_colors
        for galaxy in galaxy_list:
            if accumulated_wall_time + time_fit >= wall_time:
                partitioned_list.append(sub_list)
                sub_list = []
                accumulated_wall_time = time_infrared_colors + time_optical_colors
            sub_list.append(galaxy)
            accumulated_wall_time += time_fit

    partitioned_list.append(sub_list)
    return partitioned_list


def write_out_galaxies(**kwargs):
    galaxies_by_red_shift = kwargs['galaxies_by_red_shift']
    dir_out_root_name = kwargs['dir_out_root_name']
    dir_magphys = kwargs['dir_magphys']
    run = kwargs['run']
    magphys_library = kwargs['magphys_library']
    get_infrared_colors = kwargs['get_infrared_colors']
    time_infrared_colors = kwargs['time_infrared_colors']
    time_optical_colors = kwargs['time_optical_colors']
    time_fit = kwargs['time_fit']
    wall_time = kwargs['wall_time'] - 10

    directory_counter = 0
    output_file = None

    accumulated_wall_time = 0
    LOG.info('{0} entries to process'.format(len(galaxies_by_red_shift.keys())))
    for redshift in sorted(galaxies_by_red_shift):
        galaxy_list = galaxies_by_red_shift[redshift]
        LOG.info('Looking at redshift:{0} galaxies:{1}'.format(redshift, len(galaxy_list)))

        # Partition the list
        partitioned_list = partition_list(galaxy_list, time_infrared_colors, time_optical_colors, time_fit, wall_time, accumulated_wall_time)

        for index in range(0, len(partitioned_list)):
            list_of_galaxies = partitioned_list[index]
            # Do we need to close the file down?
            if len(list_of_galaxies) == 0 and output_file is not None:
                output_file.close()
                output_file = None
                continue

            if output_file is None:
                output_file, directory_name = open_outputfile(dir_out_root_name, directory_counter)
                write_header(output_file, directory_name, dir_magphys, run, magphys_library)
                directory_counter += 1

            # Check if we need to build models
            write_check_we_have_something_to_do(output_file, list_of_galaxies)

            write_data_file(output_file, redshift, list_of_galaxies)
            write_model_generation(output_file, redshift, get_infrared_colors)
            accumulated_wall_time += time_infrared_colors + time_optical_colors
            galaxy_id = 1
            for line in list_of_galaxies:
                write_run_magphys(output_file, galaxy_id, line[0])
                galaxy_id += 1
                accumulated_wall_time += time_fit

            write_fi(output_file)
            write_rm_lbr(output_file)

            # Make sure we don't close the last one
            if index < len(partitioned_list) - 1:
                output_file.close()
                output_file = None

    # Close the last file
    if output_file is not None:
        output_file.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dat_file_name', nargs=1, help='the dat file to use')
    parser.add_argument('dir_out_root_name', nargs=1, help='where the files are written')
    parser.add_argument('magphys', nargs=1, help='where the magphys files are to be found')
    parser.add_argument('run', nargs=1, help='where the filters.dat file is to be found')
    parser.add_argument('magphys_library', nargs=1, help='which MAGPHYS optical library to use', choices=['cb07', 'bc03'])
    parser.add_argument('--get_infrared_colors', help='the get_infrared_colors executable name', default='get_infrared_colors')
    parser.add_argument('--time_infrared_colors', type=int, help='the time (in minutes) for get_infrared_colors to run', default=5)
    parser.add_argument('--time_optical_colors', type=int, help='the time (in minutes) for get_optical_colors to run', default=5)
    parser.add_argument('--time_fit', type=int, help='the time to perform a fit', default=6)
    parser.add_argument('--wall_time', type=int, help='the wall time (in minutes)', default=180)
    parser.add_argument('--has_header_row', action='store_true', help='does the input file have a header row', default=False)
    parser.add_argument('--separator', help='what separator does the file use', default=',')
    args = parser.parse_args()

    if not check_exists(args.dat_file_name[0], args.dir_out_root_name[0]):
        return

    galaxies_by_red_shift = get_galaxies_by_red_shift(args.dat_file_name[0], args.has_header_row, args.separator)

    write_out_galaxies(
        galaxies_by_red_shift=galaxies_by_red_shift,
        dir_out_root_name=args.dir_out_root_name[0],
        dir_magphys=args.magphys[0],
        run=args.run[0],
        magphys_library=args.magphys_library[0],
        get_infrared_colors=args.get_infrared_colors,
        time_infrared_colors=args.time_infrared_colors,
        time_optical_colors=args.time_optical_colors,
        time_fit=args.time_fit,
        wall_time=args.wall_time,
    )


if __name__ == "__main__":
    main()
