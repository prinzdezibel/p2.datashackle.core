# -*- coding: utf-8 -*-

import random

from sqlalchemy import *
from migrate import *
from migrate.changeset import *

mod = __import__('001_initial_schema')
p2_plan = getattr(mod, 'p2_plan')
p2_country = getattr(mod, 'p2_country')

#metadata = MetaData()


def upgrade(migrate_engine):
 #   metadata.bind = migrate_engine

 #  p2_country.create()
    p2_country.insert().execute(
        id=migrate_engine.generate_random_identifier(),
        country_name='Germany',
        country_iso_code_2='DE',
        country_iso_code_3="DEU"
    )
    p2_country.insert().execute(
        id=migrate_engine.generate_random_identifier(),
        country_name='France',
        country_iso_code_2='FR',
        country_iso_code_3="FRA"
    )
    p2_country.insert().execute(
        id=migrate_engine.generate_random_identifier(),
        country_name='Denmark',
        country_iso_code_2='DK',
        country_iso_code_3="DNK"
    )

    

def downgrade(migrate_engine):
    pass

