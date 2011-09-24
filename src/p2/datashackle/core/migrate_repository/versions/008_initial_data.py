# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2010-2011
# Author:  Michael Jenny <michael.jenny%40projekt-und-partner.com>

import random
import pdb
import os.path

from sqlalchemy import *
from migrate import *
from migrate.changeset import *

# Relative path imports are not possible. Therefore this workaround that allows them
# (paths will be relative to this script's container directory (NOT the current working dir!))
def importrelativescript(path):
    import os,sys
    scriptdir = os.path.dirname(__file__)
    if scriptdir.endswith('/') == False: scriptdir += "/"
    sys.path.append(scriptdir + path[:path.rfind("/")])
    try:
        project = __import__(os.path.basename(scriptdir + path))
    finally:
        del sys.path[-1]
    return project


# Explanation: from 001_initial_schema import *
# does obviously not work because the module name starts with a digit.
# But this is probably by design and sqlalchemy migrate requires that.
# The workaround is as follows:
mod = __import__('001_initial_schema')

data = mod.upgradedataobj()
data.p2_plan = getattr(mod, 'p2_plan')
data.p2_form = getattr(mod, 'p2_form')
data.p2_widget = getattr(mod, 'p2_widget')
data.p2_span = getattr(mod, 'p2_span')
data.p2_linkage = getattr(mod, 'p2_linkage')
data.p2_span_relation = getattr(mod, 'p2_span_relation')
data.p2_span_fileupload = getattr(mod, 'p2_span_fileupload')
data.p2_span_action = getattr(mod, 'p2_span_action')
data.p2_span_alphanumeric = getattr(mod, 'p2_span_alphanumeric')
data.p2_span_checkbox = getattr(mod, 'p2_span_checkbox')
data.p2_span_dropdown = getattr(mod, 'p2_span_dropdown')
data.cardinalities = getattr(__import__('003_cardinalities'), 'cardinalitydict')



def upgrade(migrate_engine):


    # --- DUMMY DATA (for testing)
    insStmt = data.p2_plan.insert()
    result = insStmt.execute(plan_identifier='test',
                             so_module='p2.datashackle.core.models.setobject_types',
                             so_type='test')
    plan_id = result.inserted_primary_key[0]
    result = data.p2_form.insert().execute(active=True,
        height=400,
        width=500,
        form_identifier=data.generate_random_identifier(),
        form_name="default_form",
        fk_p2_plan=plan_id
        )
    form_id = result.inserted_primary_key[0]
    data.p2_plan.update().where(data.p2_plan.c.plan_identifier == plan_id).execute(fk_default_form=form_id)
    


def downgrade(migrate_engine):
    pass
