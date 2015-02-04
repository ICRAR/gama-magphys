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
The SQL Alchemy definitions
"""
from sqlalchemy import MetaData, Table, Column, Integer, Numeric, String, TIMESTAMP, Float, BigInteger, ForeignKey

MAGPHYS_METADATA = MetaData()

PARAMETER_NAME = Table('parameter_name',
                       MAGPHYS_METADATA,
                       Column('parameter_name_id', BigInteger, primary_key=True),
                       Column('name', String(100), nullable=False),
                       Column('create_time', TIMESTAMP, nullable=False)
                       )

RUN = Table('run',
            MAGPHYS_METADATA,
            Column('run_id', BigInteger, primary_key=True),
            Column('description', String(1000), nullable=False),
            Column('create_time', TIMESTAMP, nullable=False)
            )

GALAXY = Table('galaxy',
               MAGPHYS_METADATA,
               Column('galaxy_id', BigInteger, primary_key=True),
               Column('run_id', BigInteger, ForeignKey('run.run_id')),
               Column('gama_id', String(256), nullable=False),
               Column('redshift', Numeric(10, 7), nullable=False),
               Column('i_sfh', Float, nullable=False),
               Column('i_ir', Float, nullable=False),
               Column('chi2', Float, nullable=False),
               Column('create_time', TIMESTAMP, nullable=False)
               )

FILTER = Table('filter',
               MAGPHYS_METADATA,
               Column('filter_id', BigInteger, primary_key=True),
               Column('run_id', BigInteger, ForeignKey('run.run_id')),
               Column('name', String(30), nullable=False),
               Column('eff_lambda', Numeric(10, 4), nullable=False),
               Column('filter_number', Integer, nullable=False),
               Column('create_time', TIMESTAMP, nullable=False)
               )

FILTER_VALUE = Table('filter_value',
                     MAGPHYS_METADATA,
                     Column('filter_values_id', BigInteger, primary_key=True),
                     Column('filter_id', BigInteger, ForeignKey('filter.filter_id')),
                     Column('galaxy_id', BigInteger, ForeignKey('galaxy.galaxy_id')),
                     Column('flux', Float, nullable=False),
                     Column('sigma', Float, nullable=False),
                     Column('flux_bfm', Float, nullable=False),
                     Column('create_time', TIMESTAMP, nullable=False)
                     )

RESULT = Table('result',
               MAGPHYS_METADATA,
               Column('parameter_result_id', BigInteger, primary_key=True),
               Column('galaxy_id', BigInteger, ForeignKey('galaxy.galaxy_id')),
               Column('parameter_name_id', Integer, nullable=False),
               Column('best_fit', Float, nullable=True),
               Column('percentile2_5', Float, nullable=False),
               Column('percentile16', Float, nullable=False),
               Column('percentile50', Float, nullable=False),
               Column('percentile84', Float, nullable=False),
               Column('percentile97_5', Float, nullable=False),
               Column('create_time', TIMESTAMP, nullable=False)
               )

