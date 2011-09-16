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
data.helpers = importrelativescript('widgets/helpers')

def upgrade(migrate_engine):
    global data
    
    # A plan that operates on p2_plan
    result = data.p2_plan.insert().execute(plan_identifier='p2_plan',
                             so_module='p2.setmanager.models.plan',
                             so_type='Plan')
    plan_id = result.inserted_primary_key[0]
    
    insStmt = data.p2_form.insert()
    result = insStmt.execute(active=True,
                             height=40,
                             width=410,
                             form_identifier=data.generate_random_identifier(),
                             form_name="plans",
                             fk_p2_plan=plan_id)
    form_id = result.inserted_primary_key[0]
    data.helpers.create_labeltext_widget(data, form_id, 0, 0, 'Setobject module', 'so_module', None, tab_order=0, text_width=250)
    data.helpers.create_labeltext_widget(data, form_id, 0, 20, 'Setobject class name', 'so_type', None, tab_order=1, text_width=250)
   
    data.p2_plan.update().where(data.p2_plan.c.plan_identifier == plan_id).execute(fk_default_form=form_id) 

def downgrade(migrate_engine):
    pass
