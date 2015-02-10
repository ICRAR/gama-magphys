#! /usr/bin/env python
#
#    (c) UWA, The University of Western Australia
#    M468/35 Stirling Hwy
#    Perth WA 6009
#    Australia
#
#    Copyright by UWA, 2012
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
Process the gama files
"""
import argparse
import glob
import logging
import os
from sqlalchemy import create_engine, select, and_
from configuration import DB_LOGIN
from database import FILTER, PARAMETER_NAME, GALAXY, RESULT, FILTER_VALUE
from process_magphys_file import ProcessMagphysFile

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)-15s:' + logging.BASIC_FORMAT)


def get_maps(connection, run_id):
    # Load the filters
    map_filter = {}
    for filter_used in connection.execute(select([FILTER]).where(FILTER.c.run_id == run_id)):
        map_filter[filter_used[FILTER.c.name]] = filter_used[FILTER.c.filter_id]

    # Load the parameter name map
    map_parameter_name = {}
    for parameter_name in connection.execute(select([PARAMETER_NAME])):
        map_parameter_name[parameter_name[PARAMETER_NAME.c.name]] = parameter_name[PARAMETER_NAME.c.parameter_name_id]

    return map_filter, map_parameter_name


def store_data(connection, run_id, galaxy, list_filter_values, map_results, insert_galaxy, insert_filter_value, insert_result):
    """
    Now store the data
    """
    transaction = connection.begin()

    try:
        # Insert the galaxy
        result = connection.execute(insert_galaxy,
                                    run_id=run_id,
                                    gama_id=galaxy.gama_id,
                                    redshift=galaxy.redshift,
                                    i_sfh=galaxy.i_sfh,
                                    i_ir=galaxy.i_ir,
                                    chi2=galaxy.chi2
                                    )
        galaxy_id = result.inserted_primary_key[0]

        for filter_value in list_filter_values:
            connection.execute(insert_filter_value,
                               galaxy_id=galaxy_id,
                               filter_id=filter_value.filter_id,
                               flux=filter_value.flux,
                               sigma=filter_value.sigma,
                               flux_bfm=filter_value.flux_bfm,
                               )

        for result in map_results.values():
            connection.execute(insert_result,
                               galaxy_id=galaxy_id,
                               parameter_name_id=result.parameter_name_id,
                               best_fit=result.best_fit,
                               percentile2_5=result.percentile2_5,
                               percentile16=result.percentile16,
                               percentile50=result.percentile50,
                               percentile84=result.percentile84,
                               percentile97_5=result.percentile97_5,
                               )
        transaction.commit()
    except Exception:
        LOG.exception('Insert error')
        if transaction is not None:
            transaction.rollback()


def get_gama_id(result_file):
    path, filename = os.path.split(result_file)
    gama_id, ext = os.path.splitext(filename)
    return gama_id


def need_to_process(connection, gama_id, run_id):
    galaxy = connection.execute(select([GALAXY]).where(and_(GALAXY.c.gama_id == gama_id, GALAXY.c.run_id == run_id))).first()
    return galaxy is None


def main(run_id, directory):
    db_login = "{0}".format(DB_LOGIN)
    engine = create_engine(db_login)
    connection = engine.connect()

    map_filter, map_parameter_name = get_maps(connection, run_id)
    process_magphys = ProcessMagphysFile(map_filter, map_parameter_name)
    insert_galaxy = GALAXY.insert()
    insert_filter_value = FILTER_VALUE.insert()
    insert_result = RESULT.insert()

    for result_file in glob.glob(directory + '/*.f*'):
        LOG.info('Looking at: {0}'.format(result_file))
        gama_id = get_gama_id(result_file)
        if need_to_process(connection, gama_id, run_id):
            LOG.info('The file {0} needs processing'.format(result_file))
            galaxy, list_filter_values, map_results = process_magphys.process_file(gama_id, result_file)
            store_data(connection, run_id, galaxy, list_filter_values, map_results, insert_galaxy, insert_filter_value, insert_result)
            LOG.info('Completed: {0}'.format(result_file))
        else:
            LOG.info('Skipping: {0}'.format(result_file))

    connection.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('run_id', type=int, nargs=1, help='the run id')
    parser.add_argument('directory', nargs=1, help='the directory with the files')

    args = vars(parser.parse_args())

    main(args['run_id'][0], args['directory'][0])
