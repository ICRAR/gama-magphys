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
Read the timings file
"""
import argparse
import glob
import os

import logging
import pandas

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)-15s:' + logging.BASIC_FORMAT)


class ReadTimings:
    def __init__(self, root_directory_name):
        self._root_directory_name = root_directory_name
        self._final_data_frame = None

    def read(self):
        for file_name in glob.glob(os.path.join(self._root_directory_name, '*/timings.csv')):
            LOG.info('Reading {0}'.format(file_name))
            # Read the data from the CSV file
            data_frame = pandas.read_csv(file_name, header=0, skip_blank_lines=True)
            data_frame.dropna(inplace=True)

            if self._final_data_frame is None:
                self._final_data_frame = data_frame
            else:
                self._final_data_frame = self._final_data_frame.append(data_frame, ignore_index=True)

    def get_rows(self, param):
        data_frame = self._final_data_frame.loc[self._final_data_frame['task'] == param]
        return data_frame['actual']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root_directory_name', nargs=1, help='the top of the directory hierarchy to use')
    args = parser.parse_args()

    read_timings = ReadTimings(args.root_directory_name[0])
    read_timings.read()

    for parameter in ['fit', 'get_optic_colors', 'get_infrared_colors_smaddox']:
        data_frame = read_timings.get_rows(parameter)
        LOG.info('\n{0}\n{1}'.format(parameter, data_frame.describe()))

if __name__ == "__main__":
    main()
