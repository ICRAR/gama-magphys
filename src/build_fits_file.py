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
Extract the data from the database and add it to a fits file
"""
import argparse
import logging
import pyfits
from sqlalchemy import create_engine, func, select
from database import GALAXY, PARAMETER_NAME, RESULT

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)-15s:' + logging.BASIC_FORMAT)

VALUES = ['best_fit', 'percentile2_5', 'percentile16', 'percentile50', 'percentile84', 'percentile97_5']


def create_hdu(rows, map_parameter_name):
    c1 = pyfits.Column(name='gama_id', format='8A')
    c2 = pyfits.Column(name='redshift', format='E')
    columns = [c1, c2]
    for i in range(0, len(map_parameter_name)):
        for value in VALUES:
            column = pyfits.Column(name='{0}[{1}]'.format(map_parameter_name[i], value), format='E')
            columns.append(column)
    hdu = pyfits.new_table(columns, nrows=rows)
    return hdu


def load_data(connection, galaxy_id, data, count):
    field = 2
    for result in connection.execute(select([RESULT]).where(RESULT.c.galaxy_id == galaxy_id).order_by(RESULT.c.parameter_name_id)):
        data.field(field)[count] = result[RESULT.c.best_fit]
        data.field(field+1)[count] = result[RESULT.c.percentile2_5]
        data.field(field+2)[count] = result[RESULT.c.percentile16]
        data.field(field+3)[count] = result[RESULT.c.percentile50]
        data.field(field+4)[count] = result[RESULT.c.percentile84]
        data.field(field+5)[count] = result[RESULT.c.percentile97_5]
        field += len(VALUES)


def main(run_id, output_file, db_user):
    db_login = "mysql+pymysql://{0}:{0}@munro.icrar.org/gama_sed".format(db_user)
    engine = create_engine(db_login)
    connection = engine.connect()

    total = connection.execute(select([func.count(GALAXY.c.galaxy_id)]).where(GALAXY.c.run_id == run_id)).first()[0]
    map_parameter_name = {}
    for parameter_name in connection.execute(select([PARAMETER_NAME])):
        map_parameter_name[parameter_name[PARAMETER_NAME.c.parameter_name_id]] = parameter_name[PARAMETER_NAME.c.name]

    hdu = create_hdu(total, map_parameter_name)
    count = 0
    for galaxy in connection.execute(select([GALAXY]).where(GALAXY.c.run_id == run_id).order_by(GALAXY.c.gama_id)):
        if count % 1000 == 0:
            LOG.info('Processing {0} of {3}: {1}, {2}'.format(count, galaxy[GALAXY.c.gama_id], galaxy[GALAXY.c.redshift], total))
        hdu.data.field(0)[count] = galaxy[GALAXY.c.gama_id]
        hdu.data.field(1)[count] = galaxy[GALAXY.c.redshift]
        load_data(connection, galaxy[GALAXY.c.galaxy_id], hdu.data, count)
        count += 1
    hdu.writeto(output_file, clobber=True)
    connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('output', nargs=1, help='the output filename')
    parser.add_argument('run_id', type=int, nargs=1, help='the run id')
    parser.add_argument('db_user', nargs=1, help='the DB user')

    args = vars(parser.parse_args())

    main(args['run_id'][0], args['output'][0], args['db_user'][0])
