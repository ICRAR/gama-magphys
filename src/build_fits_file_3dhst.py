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
Extract the data from the database and add it to a fits file
"""
import argparse
import fnmatch
import logging
from os.path import join

import numpy
from os import walk

import astropy.io.fits as pyfits

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)-15s:' + logging.BASIC_FORMAT)


PARAMETERS = [
    'fmu (SFH)',
    'fmu (IR)',
    'mu',
    'tau_V',
    'sSFR_0.1Gyr',
    'M(stars)',
    'Ldust',
    'T_C^ISM',
    'T_W^BC',
    'xi_C^tot',
    'xi_PAH^tot',
    'xi_MIR^tot',
    'xi_W^tot',
    'tau_V^ISM',
    'M(dust)',
    'SFR_0.1Gyr',
    'age_M',
    'log(Mstar/L_H)',
    'log(Mstar/L_K)',
    'A_V',
    'Tdust',
]
VALUES = ['best_fit', 'percentile2_5', 'percentile16', 'percentile50', 'percentile84', 'percentile97_5']


class BuildFitsFile3dhst(object):
    def __init__(self, output_file, input_root):
        self._map_arrays = {}
        self._output_file = output_file
        self._input_root = input_root

    @staticmethod
    def _fix_numbering(filename):
        number_zeros = 12 - len(filename)
        zeros = number_zeros * '0'
        new_name = zeros + filename
        return new_name

    def _get_files_to_read(self):
        self._files_to_process = {}
        for root, dir_names, filenames in walk(self._input_root):
            for match in fnmatch.filter(filenames, '*.fit'):
                result_file = join(root, match)
                elements = root.split('/')
                key = join(elements[-2], self._fix_numbering(match))
                self._files_to_process[key] = result_file

    def _create_fits_file(self):
        array = numpy.array(self._rows)
        columns = [
            pyfits.Column(name='3dhst_id', format='25A', array=array[:, 0]),
            pyfits.Column(name='redshift', format='E', array=array[:, 1]),
            pyfits.Column(name='i_sfh', format='J', array=array[:, 2]),
            pyfits.Column(name='i_ir', format='J', array=array[:, 3]),
            pyfits.Column(name='chi2', format='E', array=array[:, 4])
        ]

        count = 5
        for parameter in PARAMETERS:
            for value in VALUES:
                column = pyfits.Column(name='{0}[{1}]'.format(parameter, value), format='E', array=array[:, count])
                columns.append(column)
                count += 1

        hdu = pyfits.BinTableHDU.from_columns(columns)
        hdu.writeto(self._output_file, clobber=True)

    def _process_file(self, key, filename):
        row = [-99] * (len(PARAMETERS) * len(VALUES) + 5)
        line = None
        line_number = 0
        percentiles_next = False
        parameter_number = 0
        row[0] = key[:-4]
        try:
            with open(filename) as f:
                for line in f:
                    line_number += 1

                    if line_number == 9:
                        # BEST FIT MODEL: (i_sfh, i_ir, chi2, redshift)
                        # 19179      3829    12.123    1.035000
                        best_fit = line.split()
                        if len(best_fit) == 4:
                            row[2] = int(best_fit[0])
                            row[3] = int(best_fit[1])
                            row[4] = float(best_fit[2])
                            row[1] = float(best_fit[3])
                        else:
                            LOG.warning('Only {0} arguments from line: {1}'.format(len(best_fit), line))
                            if len(best_fit) == 3 and best_fit[1].startswith('0') and best_fit[1].endswith('*'):
                                row[1] = int(best_fit[0])
                                row[2] = 0
                                row[3] = 0.0
                                row[4] = float(best_fit[2])
                    elif line_number == 11:
                        best_fits = line.split()
                        row[5 + (0 * len(VALUES))] = float(best_fits[0])    # fmu(SFH)
                        row[5 + (1 * len(VALUES))] = float(best_fits[1])    # fmu(IR)
                        row[5 + (2 * len(VALUES))] = float(best_fits[2])    # mu
                        row[5 + (3 * len(VALUES))] = float(best_fits[3])    # tauv
                        row[5 + (4 * len(VALUES))] = float(best_fits[4])    # sSFR
                        row[5 + (5 * len(VALUES))] = float(best_fits[5])    # M*
                        row[5 + (6 * len(VALUES))] = float(best_fits[6])    # Ldust
                        row[5 + (7 * len(VALUES))] = float(best_fits[8])    # T_C^ISM
                        row[5 + (8 * len(VALUES))] = float(best_fits[7])    # T_W^BC
                        row[5 + (9 * len(VALUES))] = float(best_fits[9])    # xi_C^tot
                        row[5 + (10 * len(VALUES))] = float(best_fits[10])  # xi_PAH^tot
                        row[5 + (11 * len(VALUES))] = float(best_fits[11])  # xi_MIR^tot
                        row[5 + (12 * len(VALUES))] = float(best_fits[12])  # xi_W^tot
                        row[5 + (13 * len(VALUES))] = float(best_fits[13])  # tvism
                        row[5 + (14 * len(VALUES))] = float(best_fits[14])  # Mdust
                        row[5 + (15 * len(VALUES))] = float(best_fits[15])  # SFR
                        row[5 + (16 * len(VALUES))] = float(best_fits[17])  # age_M
                        row[5 + (17 * len(VALUES))] = float(best_fits[19])  # lg(M/Lh)
                        row[5 + (18 * len(VALUES))] = float(best_fits[20])  # lg(M/Lk)
                        row[5 + (19 * len(VALUES))] = float(best_fits[16])  # A_V
                        row[5 + (20 * len(VALUES))] = float(best_fits[18])  # Tdust

                    elif line_number >= 16:
                        if line.startswith("#....percentiles of the PDF......"):
                            percentiles_next = True

                        elif percentiles_next:
                            values = line.split()
                            offset = 5 + (parameter_number * 6) + 1
                            row[offset] = float(values[0])
                            row[offset + 1] = float(values[1])
                            row[offset + 2] = float(values[2])
                            row[offset + 3] = float(values[3])
                            row[offset + 4] = float(values[4])
                            percentiles_next = False
                            parameter_number += 1

        except:
            LOG.exception('''Exception after {0} lines
{1}'''.format(line_number, line))

        self._rows.append(row)

    def _process_files(self):
        self._rows = []
        keys = sorted(self._files_to_process.keys())
        for key in keys:
            self._process_file(key, self._files_to_process[key])

    def build_file(self):
        self._get_files_to_read()
        self._process_files()
        self._create_fits_file()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('output', nargs=1, help='the output filename')
    parser.add_argument('input_root', nargs=1, help='root directory to search')

    args = vars(parser.parse_args())

    build = BuildFitsFile3dhst(args['output'][0], args['input_root'][0])
    build.build_file()
