# -*- coding: utf-8 -*-

import random

from sqlalchemy import *
from migrate import *
from migrate.changeset import *

mod = __import__('001_initial_schema')
p2_plan = getattr(mod, 'p2_plan')

def generate_random_identifier():
    n_id = random.randint(0, 100000000)
    id = "%08d" % n_id
    return id

metadata = MetaData()

p2_country = Table('p2_country',
   metadata,
   Column('id', String(length=8), primary_key=True, nullable=False, autoincrement=False),
   Column('country_name', String(64), nullable=False),
   Column('country_iso_code_2', CHAR(length=2), nullable=False),
   Column('country_iso_code_3', CHAR(length=3), nullable=False),
   mysql_engine='InnoDB',
)

def upgrade(migrate_engine):
    metadata.bind = migrate_engine

    p2_country.create()
    p2_country.insert().execute(
        id=generate_random_identifier(),
        country_name='Germany',
        country_iso_code_2='DE',
        country_iso_code_3="DEU"
    )
    p2_country.insert().execute(
        id=generate_random_identifier(),
        country_name='France',
        country_iso_code_2='FR',
        country_iso_code_3="FRA"
    )
    p2_country.insert().execute(
        id=generate_random_identifier(),
        country_name='Denmark',
        country_iso_code_2='DK',
        country_iso_code_3="DNK"
    )

    p2_plan.insert().execute(plan_identifier='p2_countries',
                             so_module='p2.setmanager.models.setobject_types',
                             so_type='p2_country')
    

def downgrade(migrate_engine):
    metadata.bind = migrate_engine
    p2_country.drop()


