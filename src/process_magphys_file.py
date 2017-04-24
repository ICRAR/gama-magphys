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
Process a magphys file
"""
import logging

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)-15s:' + logging.BASIC_FORMAT)


class Galaxy(object):
    def __init__(self):
        self.gama_id = None
        self.redshift = None
        self.i_sfh = None
        self.i_ir = None
        self.chi2 = None


class FilterValue(object):
    def __init__(self):
        self.filter_id = None
        self.flux = None
        self.sigma = None
        self.flux_bfm = None


class Result(object):
    def __init__(self):
        self.parameter_name_id = None
        self.best_fit = None
        self.percentile2_5 = None
        self.percentile16 = None
        self.percentile50 = None
        self.percentile84 = None
        self.percentile97_5 = None


class ProcessMagphysFile(object):
    def __init__(self, map_filter_in, map_parameter_name_in):
        # Load the filters
        self._map_filter = map_filter_in

        # Load the parameter name map
        self._map_parameter_name = map_parameter_name_in

    def process_file(self, gama_id, filename):
        """
        Process a file
        """
        # Reset a lot of the variables
        line = None
        line_number = 0
        list_filters = []
        list_filter_values = []
        map_results = {}
        parameter_name = None
        percentiles_next = False
        galaxy = Galaxy()
        galaxy.gama_id = gama_id
        for key in self._map_parameter_name.keys():
            result = Result()
            result.parameter_name_id = self._map_parameter_name[key]
            map_results[key] = result
        try:
            with open(filename) as f:
                for line in f:
                    line_number += 1

                    if line_number == 2:
                        filter_names = line.split()
                        list_filters = filter_names[1:]

                    elif line_number == 3:
                        fluxes = line.split()
                        i = 0
                        for flux in fluxes:
                            filter_value = FilterValue()
                            filter_name = list_filters[i]
                            filter_value.filter_id = self._map_filter[filter_name]
                            filter_value.flux = flux
                            list_filter_values.append(filter_value)
                            i += 1

                    elif line_number == 4:
                        sigmas = line.split()
                        i = 0
                        for sigma in sigmas:
                            filter_value = list_filter_values[i]
                            filter_value.sigma = sigma
                            i += 1

                    elif line_number == 9:
                        best_fit = line.split()
                        if len(best_fit) == 4:
                            galaxy.i_sfh = best_fit[0]
                            galaxy.i_ir = best_fit[1]
                            galaxy.chi2 = best_fit[2]
                            galaxy.redshift = best_fit[3]
                        else:
                            galaxy.i_sfh = 0
                            galaxy.i_ir = 0
                            galaxy.chi2 = 0
                            galaxy.redshift = 0
                            LOG.warning('Only {0} arguments from line: {1}'.format(len(best_fit), line))
                            if len(best_fit) == 3 and best_fit[1].startswith('0') and best_fit[1].endswith('*'):
                                galaxy.i_sfh = best_fit[0]
                                galaxy.i_ir = 0
                                galaxy.chi2 = 0
                                galaxy.redshift = best_fit[2]
                    elif line_number == 11:
                        best_fits = line.split()
                        map_results['f_mu (SFH)'].best_fit = best_fits[0]
                        map_results['f_mu (IR)'].best_fit = best_fits[1]
                        map_results['mu parameter'].best_fit = best_fits[2]
                        map_results['tau_V'].best_fit = best_fits[3]
                        map_results['sSFR_0.1Gyr'].best_fit = best_fits[4]
                        map_results['M(stars)'].best_fit = best_fits[5]
                        map_results['Ldust'].best_fit = best_fits[6]
                        map_results['T_W^BC'].best_fit = best_fits[7]
                        map_results['T_C^ISM'].best_fit = best_fits[8]
                        map_results['xi_C^tot'].best_fit = best_fits[9]
                        map_results['xi_PAH^tot'].best_fit = best_fits[10]
                        map_results['xi_MIR^tot'].best_fit = best_fits[11]
                        map_results['xi_W^tot'].best_fit = best_fits[12]
                        map_results['tau_V^ISM'].best_fit = best_fits[13]
                        map_results['M(dust)'].best_fit = best_fits[14]
                        map_results['SFR_0.1Gyr'].best_fit = best_fits[15]

                    elif line_number == 13:
                        bfms = line.split()
                        i = 0
                        for bfm in bfms:
                            filter_value = list_filter_values[i]
                            filter_value.flux_bfm = bfm
                            i += 1

                    elif line_number >= 16:
                        if line.startswith("# ..."):
                            parts = line.split('...')
                            parameter_name = parts[1].strip()

                        elif line.startswith("#....percentiles of the PDF......"):
                            percentiles_next = True

                        elif percentiles_next:
                            values = line.split()
                            result = map_results[parameter_name]
                            result.percentile2_5 = values[0]
                            result.percentile16 = values[1]
                            result.percentile50 = values[2]
                            result.percentile84 = values[3]
                            result.percentile97_5 = values[4]
                            percentiles_next = False

        except:
            LOG.exception('''Exception after {0} lines
{1}'''.format(line_number, line))

        return galaxy, list_filter_values, map_results


if __name__ == "__main__":
    map_filter = {
        'fuv': 0,
        'nuv': 1,
        'u': 2,
        'g': 3,
        'r': 4,
        'i': 5,
        'Z': 6,
        'Y': 7,
        'J': 8,
        'H': 9,
        'K': 10,
        'WISEW1': 11,
        'WISEW2': 12,
        'WISEW3': 13,
        'WISEW4': 14,
        'PACS100': 15,
        'PACS160': 16,
        'SPIRE250': 17,
        'SPIRE350': 18,
        'SPIRE500': 19,
    }
    map_parameter_name = {
        'f_mu (SFH)': 0,
        'f_mu (IR)': 1,
        'mu parameter': 2,
        'tau_V': 3,
        'sSFR_0.1Gyr': 4,
        'M(stars)': 5,
        'Ldust': 6,
        'T_C^ISM': 7,
        'T_W^BC': 8,
        'xi_C^tot': 9,
        'xi_PAH^tot': 10,
        'xi_MIR^tot': 11,
        'xi_W^tot': 12,
        'tau_V^ISM': 13,
        'M(dust)': 14,
        'SFR_0.1Gyr': 15,
        'metalicity Z/Zo': 16,
        'tform': 17,
        'gamma': 18,
        'tlastb': 19,
        'agem': 20,
        'ager': 21,
        'sfr16': 22,
        'sfr17': 23,
        'sfr18': 24,
        'sfr19': 25,
        'sfr29': 26,
        'fb16': 27,
        'fb17': 28,
        'fb18': 29,
        'fb19': 30,
        'fb29': 31,
    }
    process_magphys = ProcessMagphysFile(map_parameter_name, map_filter)
    process_magphys.process_file('00343593', '../data/00343593.f')
    process_magphys.process_file('00861737', '../data/00861737.f')
