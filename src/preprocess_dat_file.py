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
from decimal import Decimal
import logging
import os


LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)-15s:' + logging.BASIC_FORMAT)

_0001 = Decimal('.0001')
_0 = Decimal('0.0')
_6 = Decimal('6.0')


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


def write_run_magphys(output_file, galaxy_id, galaxy_number):
    output_file.write('''
START=$(date +%s)
if [ ! -f {2} ]; then
  echo "processing {0} - {1}"
  echo {0} | $magphys/fit_sed_zz2_uplimits
else
  echo "skipping {0} - {1}"
fi
END=$(date +%s)
DIFF=$(echo "$END - $START" | bc)
echo $DIFF seconds
'''.format(galaxy_id, galaxy_number, ten_char_filename(galaxy_number, 'sed')))


def ten_char_filename(file_stem, extension):
    filename = '{0}.{1}'.format(file_stem, extension)
    return filename


def write_model_generation(output_file, redshift, get_infrared_colors):
    output_file.write('''
START=$(date +%s)
# Create the models
echo "{0}
70.0,0.3,0.7" > redshift

echo N | $magphys/make_zgrid
cat redshift | $magphys/get_optic_colors
cat redshift | $magphys/{1}

END=$(date +%s)
DIFF=$(echo "$END - $START" | bc)
echo $DIFF seconds

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
        elements = line.split()
        if add_or:
            output_file.write(' || ')
        output_file.write('[ ! -f {0} ]'.format(ten_char_filename(elements[0], 'sed')))
        add_or = True

    output_file.write('''; then

''')


def write_rm_lbr(output_file):
    output_file.write('''
# Remove any models
/bin/rm -f *.lbr
''')


def write_data_file(output_file, redshift, lines):
    output_file.write('''
# Next galaxies
echo "# Header" > mygals.dat
''')
    for line in lines:
        elements = line.split()
        # Need the 4 digit redshift
        output_file.write('echo "{0} {1}'.format(elements[0], redshift))

        for element in elements[2:]:
            output_file.write(' {0}'.format(element))
        output_file.write('''" >> mygals.dat
'''.format(line))


def partition_list(galaxy_list, partition_size):
    counter = 0
    partitioned_list = []
    sub_list = []
    for galaxy in galaxy_list:
        if counter % partition_size == 0 and counter > 0:
            partitioned_list.append(sub_list)
            sub_list = []
        sub_list.append(galaxy)
        counter += 1

    partitioned_list.append(sub_list)
    return partitioned_list


def close_old_and_open_new(dir_root_name, directory_counter, output_file, magphys_directory, run, magphys_library):
    if output_file is not None:
        output_file.close()

    if directory_counter is None:
        directory_counter = 0
    else:
        directory_counter += 1

    directory_name = os.path.join(dir_root_name, '{0:06d}'.format(directory_counter))
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

    file_name = os.path.join(directory_name, 'process_data.sh')
    LOG.info('Creating {0}'.format(file_name))
    output_file = open(file_name, 'w')
    write_header(output_file, directory_name, magphys_directory, run, magphys_library)
    return directory_counter, 0, output_file


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dat_file_name', nargs=1, help='the dat file to use')
    parser.add_argument('dir_root_name', nargs=1, help='where the files are written')
    parser.add_argument('magphys', nargs=1, help='where the magphys files are to be found')
    parser.add_argument('run', nargs=1, help='where the filters.dat file is to be found')
    parser.add_argument('magphys_library', nargs=1, help='which MAGPHYS optical library to use', choices=['cb07', 'bc03'])
    parser.add_argument('--get_infrared_colors', help='the get_infrared_colors executable name', default='get_infrared_colors')
    parser.add_argument('--galaxies_per_directory', type=int, help='how many galaxies per directory', default=20)
    parser.add_argument('--partition_size', type=int, help='the partition size ', default=40)
    args = vars(parser.parse_args())

    dat_file_name = args['dat_file_name'][0]
    dir_root_name = args['dir_root_name'][0]
    magphys_directory = args['magphys'][0]
    magphys_library = args['magphys_library'][0]
    run = args['run'][0]
    get_infrared_colors = args['get_infrared_colors'][0]
    galaxies_per_directory = args['galaxies_per_directory'][0]
    partition_size = args['partition_size'][0]

    if not os.path.exists(dat_file_name):
        LOG.error('The file {0} does not exist'.format(dat_file_name))
        return

    if not os.path.isdir(dir_root_name):
        LOG.error('The directory {0} does not exist'.format(dir_root_name))
        return

    LOG.info('Reading {0}'.format(dat_file_name))
    galaxies_by_red_shift = {}

    with open(dat_file_name, 'r') as dat_file:
        line_number = 1
        for line in dat_file:
            # remove whitespace
            line = line.strip()

            # Parse the line to remove bogus redshifts
            elements = line.split()

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

                    list_of_galaxies.append(line)
            except Exception:
                LOG.exception('Error processing line {0} - {1}'.format(line_number, line))

            line_number += 1

    directory_counter = None
    line_counter = 0
    output_file = None
    LOG.info('{0} entries to process'.format(len(galaxies_by_red_shift.keys())))
    for key in sorted(galaxies_by_red_shift):
        galaxy_list = galaxies_by_red_shift[key]
        LOG.info('Looking at redshift:{0} galaxies:{1}'.format(key, len(galaxy_list)))
        # Partition the list
        partitioned_list = partition_list(galaxy_list, partition_size)

        if len(partitioned_list) > 1 and output_file is not None:
            # Close the previous file
            directory_counter, line_counter, output_file = close_old_and_open_new(
                dir_root_name,
                directory_counter,
                output_file,
                magphys_directory,
                run,
                magphys_library)

        for list_of_galaxies in partitioned_list:
            # Do we need a new output file
            if line_counter >= galaxies_per_directory or output_file is None:
                # noinspection PyTypeChecker
                directory_counter, line_counter, output_file = close_old_and_open_new(
                    dir_root_name,
                    directory_counter,
                    output_file,
                    magphys_directory,
                    run,
                    magphys_library)

            # Check if we need to build models
            write_check_we_have_something_to_do(output_file, list_of_galaxies)

            write_data_file(output_file, key, list_of_galaxies)
            write_model_generation(output_file, key, get_infrared_colors)
            galaxy_id = 1
            for line in list_of_galaxies:
                elements = line.split()
                write_run_magphys(output_file, galaxy_id, elements[0])
                line_counter += 1
                galaxy_id += 1

            write_fi(output_file)
            write_rm_lbr(output_file)

    # Close the last file
    if output_file is not None:
        output_file.close()

if __name__ == "__main__":
    # ../magphys/run02/forkevin.csv /tmp/run /group/partner1024/kvinsen/gama-magphys/magphys run02 cb07
    # ../magphys/ned01/lambdar_variations.cat /tmp/run /group/partner1024/kvinsen/gama-magphys/magphys run02 cb07
    # ../magphys/run03/forkevin.csv /tmp/run /group/partner1024/kvinsen/gama-magphys/magphys run03 bc03
    main()
