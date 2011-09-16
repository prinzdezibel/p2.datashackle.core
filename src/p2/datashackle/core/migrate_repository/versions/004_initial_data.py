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

data.helpers = importrelativescript('widgets/helpers')
labeltext = importrelativescript('widgets/labeltext')
checkbox = importrelativescript('widgets/checkbox')
fileupload = importrelativescript('widgets/fileupload')
relation = importrelativescript('widgets/relation')
dropdown = importrelativescript('widgets/dropdown')

def upgrade(migrate_engine):
    global data

    # --- ARCHETYPE FORM ---
    
    insStmt = data.p2_plan.insert()
    result = insStmt.execute(plan_identifier='p2_archetype',   
                             so_module='p2.datashackle.core.models.setobject_types',
                             so_type='p2_archetype')
    last_inserted_id = result.inserted_primary_key[0]
    data.archetype_plan_id = last_inserted_id
    
    insStmt = data.p2_form.insert()
    result = insStmt.execute(active=True,
                         height=300,
                         width=230,
                         form_identifier=data.generate_random_identifier(),
                         form_name="archetypes",
                         fk_p2_plan=last_inserted_id)
    last_inserted_id = result.inserted_primary_key[0]
    data.archetype_form_id = last_inserted_id
    
    

    # --- INITIAL LINKAGES ---
    # Add initial linkages
    
    # plan -> default_form
    insStmt = data.p2_linkage.insert()
    result = insStmt.execute(id=data.generate_random_identifier(),
                             attr_name='default_form',
                             ref_type='object',
                             ref_key=None,
                             foreignkeycol='fk_default_form',
                             source_module='p2.datashackle.core.models.plan',
                             source_classname='Plan',
                             target_classname='FormType',
                             target_module='p2.datashackle.core.models.form',
                             fk_cardinality=data.cardinalities['n:1'],
                             cascade='save-update, merge',
                             post_update=True, #http://www.sqlalchemy.org/docs/05/mappers.html#rows-that-point-to-themselves-mutually-dependent-rows
                             )
    
    # plan -> forms[fk]
    insStmt = data.p2_linkage.insert()
    result = insStmt.execute(id=data.generate_random_identifier(),
                             attr_name='forms',
                             ref_type='dict',
                             ref_key='form_name',
                             foreignkeycol='fk_p2_plan',
                             source_module='p2.datashackle.core.models.plan',
                             source_classname='Plan',
                             target_classname='FormType',
                             target_module='p2.datashackle.core.models.form',
                             back_populates='plan',
                             fk_cardinality=data.cardinalities['1:n'],
                             cascade='save-update, merge')
    
    # plan -> forms[fk] (backref)
    result = insStmt.execute(id=data.generate_random_identifier(),
                             attr_name='plan',
                             ref_type='object',
                             foreignkeycol='fk_p2_plan',
                             back_populates='forms',
                             source_module='p2.datashackle.core.models.form',
                             source_classname='FormType',
                             target_classname='Plan',
                             target_module='p2.datashackle.core.models.plan',
                             fk_cardinality=data.cardinalities['n:1'],
                             cascade='all')
                             
    # form -> widgets[fk]
    result = insStmt.execute(id=data.generate_random_identifier(),
                             attr_name='widgets',
                             ref_type='dict',
                             foreignkeycol='fk_p2_form',
                             source_module='p2.datashackle.core.models.form',
                             source_classname='FormType',
                             target_classname='WidgetType',
                             target_module='p2.datashackle.core.models.widget.widget',
                             back_populates='form',
                             fk_cardinality=data.cardinalities['1:n'],
                             cascade='save-update, merge')
                             
    # widget[fk] -> form (backref)
    result = insStmt.execute(id=data.generate_random_identifier(),
                              attr_name='form',
                              ref_type='object',
                              foreignkeycol='fk_p2_form',
                              source_module='p2.datashackle.core.models.widget.widget',
                              source_classname='WidgetType',
                              target_module='p2.datashackle.core.models.form',
                              target_classname='FormType',
                              fk_cardinality=data.cardinalities['n:1'],
                              back_populates='widgets',
                              cascade='save-update, merge')
    
    # widget -> spans[fk]
    result = insStmt.execute(id=data.generate_random_identifier(),
                             attr_name='spans',
                             ref_type='dict',
                             ref_key='span_name',
                             foreignkeycol='fk_p2_widget',
                             source_module='p2.datashackle.core.models.widget.widget',
                             source_classname='WidgetType',
                             target_classname='SpanType',
                             target_module='p2.datashackle.core.models.span.span',
                             fk_cardinality=data.cardinalities['1:n'],
                             back_populates='widget',
                             cascade='all')
    data.widget_span_linkage = result.inserted_primary_key[0] 

    # span[fk] -> widget (backref)
    result = insStmt.execute(id=data.generate_random_identifier(),
                             attr_name='widget',
                             ref_type='object',
                             foreignkeycol='fk_p2_widget',
                             source_classname='SpanType',
                             source_module='p2.datashackle.core.models.span.span',
                             target_module='p2.datashackle.core.models.widget.widget',
                             target_classname='WidgetType',
                             fk_cardinality=data.cardinalities['n:1'],
                             back_populates='spans',
                             cascade='save-update, merge'
                             )

    # p2_span_relation -> p2_linkage
    result = insStmt.execute(id=data.generate_random_identifier(),
                             attr_name='linkage',
                             ref_type='object',
                             foreignkeycol='fk_p2_linkage',
                             source_module='p2.datashackle.core.models.span.relation',
                             source_classname='Relation',
                             target_classname='Linkage',
                             target_module='p2.datashackle.core.models.linkage',
                             fk_cardinality=data.cardinalities['n:1'],
                             cascade='all'
                             )
    data.span_relation2linkage = result.inserted_primary_key[0]
    
    # p2_span_fileupload -> p2_linkage
    result = insStmt.execute(id=data.generate_random_identifier(),
                             attr_name='linkage',
                             ref_type='object',
                             foreignkeycol='fk_p2_linkage',
                             source_module='p2.datashackle.core.models.span.fileupload',
                             source_classname='Fileupload',
                             target_classname='Linkage',
                             target_module='p2.datashackle.core.models.linkage',
                             fk_cardinality=data.cardinalities['n:1'],
                             cascade='all'
                             )
    data.span_fileupload2linkage = result.inserted_primary_key[0]

    # p2_linkage plan
    result = data.p2_plan.insert().execute(plan_identifier='p2_linkage',
                             so_module='p2.datashackle.core.models.linkage',
                             so_type='Linkage')
    last_inserted_id = result.inserted_primary_key[0]
    data.linkage_plan_id = last_inserted_id

    # Widget plan
    insStmt = data.p2_plan.insert()
    result = insStmt.execute(plan_identifier='p2_widget',
                             so_module='p2.datashackle.core.models.widget.widget',
                             so_type='WidgetType')
    data.widget_plan_id = result.inserted_primary_key[0]

    # Span plan
    insStmt = data.p2_plan.insert()
    result = insStmt.execute(plan_identifier='p2_span',
                             so_module='p2.datashackle.core.models.span.span',
                             so_type='SpanType')
    data.span_plan_id = result.inserted_primary_key[0]

    #RelationSpan plan
    insStmt = data.p2_plan.insert()
    result = insStmt.execute(plan_identifier='p2_span_relation',
                             so_module='p2.datashackle.core.models.span.relation',
                             so_type='Relation')
    data.relation_span_plan_id = result.inserted_primary_key[0]

    # FileuploadSpan plan
    insStmt = data.p2_plan.insert()
    result = insStmt.execute(plan_identifier='p2_span_fileupload',
                             so_module='p2.datashackle.core.models.span.fileupload',
                             so_type='Fileupload')
    data.fileupload_span_plan_id = result.inserted_primary_key[0]

    # ActionSpan plan
    result = data.p2_plan.insert().execute(plan_identifier='p2_span_action',
                             so_module='p2.datashackle.core.models.span.span',
                             so_type='Action')
    data.action_span_plan_id = result.inserted_primary_key[0]
    
    # Alphanumeric plan
    result = data.p2_plan.insert().execute(plan_identifier='p2_span_alphanumeric',
                             so_module='p2.datashackle.core.models.span.alphanumeric',
                             so_type='Alphanumeric')
    data.alphanumeric_span_plan_id = result.inserted_primary_key[0]
    
    # Checkbox plan
    result = data.p2_plan.insert().execute(plan_identifier='p2_span_checkbox',
                             so_module='p2.datashackle.core.models.span.checkbox',
                             so_type='Checkbox')
    data.checkbox_span_plan_id = result.inserted_primary_key[0]



    data = labeltext.upgrade(migrate_engine, data)
    data = fileupload.upgrade(migrate_engine, data)
    data = checkbox.upgrade(migrate_engine, data)
    data = relation.upgrade(migrate_engine, data)
    data = dropdown.upgrade(migrate_engine, data)    



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
