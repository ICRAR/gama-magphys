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
Convert a GAMA fits file to the MAGPHYS format
"""
import argparse
import logging
import os
import pyfits

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)-15s:' + logging.BASIC_FORMAT)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('fits_file_name', nargs=1, help='the FITS file to use')
    parser.add_argument('dat_file_name', nargs=1, help='the dat file to write')
    args = vars(parser.parse_args())

    dat_file_name = args['dat_file_name'][0]
    fits_file_name = args['fits_file_name'][0]

    if not os.path.exists(fits_file_name):
        LOG.error('The file {0} does not exist'.format(fits_file_name))
        return

    LOG.info('Reading {0}'.format(fits_file_name))
    with open(dat_file_name, 'w', 1) as dat_file:
        with pyfits.open(fits_file_name, memmap=True) as hdu_list:
            # The table is in the first extension
            data = hdu_list[1].data
            length_row = data[0].end - 1
            line_count = 0
            for row in data:
                line_count += 1
                if line_count % 1000 == 0:
                    LOG.info('Read {0} lines from the FITS file'.format(line_count))

                # Ignore the last columns as it is the reference to the galaxy
                for x in range(0, length_row):
                    # Convert to a string from the Numpy type
                    dat_file.write(str(row[x]))
                    dat_file.write('  ')

                dat_file.write('\n')

if __name__ == "__main__":
    main()

