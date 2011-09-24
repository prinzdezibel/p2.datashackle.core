# -*- coding: utf-8 -*-


import random

from sqlalchemy import *
from migrate import *
from migrate.changeset import *

mod = __import__('001_initial_schema')
p2_plan = getattr(mod, 'p2_plan')
p2_cardinality = getattr(mod, 'p2_cardinality')

def generate_random_identifier():
    n_id = random.randint(0, 100000000)
    id = "%08d" % n_id
    return id

metadata = MetaData()

cardinalitydict = {}

def upgrade(migrate_engine):
    global cardinalitydict
    metadata.bind = migrate_engine
    
    migrate_engine.data['cardinalities'] = cardinalitydict = {
        '1:n' : generate_random_identifier(),
        '1(fk):1' : generate_random_identifier(),
        '1:1(fk)' : generate_random_identifier(),
        'n:1' : generate_random_identifier(),
        'n:m' : generate_random_identifier()
        }
    
    for cardinalityvalue,cardinalityid in cardinalitydict.items():
        p2_cardinality.insert().execute(
            id=cardinalityid,
            cardinality=cardinalityvalue,
        )

    p2_plan.insert().execute(plan_identifier='p2_cardinality',
                             so_module='p2.datashackle.core.models.setobject_types',
                             so_type='p2_cardinality')
    

def downgrade(migrate_engine):
    metadata.bind = migrate_engine



