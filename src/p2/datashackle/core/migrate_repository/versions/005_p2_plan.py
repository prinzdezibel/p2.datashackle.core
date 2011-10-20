# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2010-2011
# Author:  Michael Jenny <michael.jenny%40projekt-und-partner.com>

import random
import pdb
import os.path

from sqlalchemy import *
from migrate import *
from migrate.changeset import *


mod = __import__('001_initial_schema')
p2_plan = getattr(mod, 'p2_plan')
p2_form = getattr(mod, 'p2_form')


def upgrade(migrate_engine):
    
    # p2_linkage plan
    result = p2_plan.insert().execute(plan_identifier='p2_linkage',
                             so_module='p2.datashackle.core.models.linkage',
                             so_type='Linkage')
    last_inserted_id = result.inserted_primary_key[0]
    linkage_plan_id = last_inserted_id

    # Widget plan
    insStmt = p2_plan.insert()
    result = insStmt.execute(plan_identifier='p2_widget',
                             so_module='p2.datashackle.management.widget.widget',
                             so_type='WidgetType')
    widget_plan_id = result.inserted_primary_key[0]

    # Span plan
    insStmt = p2_plan.insert()
    result = insStmt.execute(plan_identifier='p2_span',
                             so_module='p2.datashackle.management.span.span',
                             so_type='SpanType')

    #RelationSpan plan
    insStmt = p2_plan.insert()
    result = insStmt.execute(plan_identifier='p2_span_relation',
                             so_module='p2.datashackle.management.span.relation',
                             so_type='Relation')
    relation_span_plan_id = result.inserted_primary_key[0]

    # FileuploadSpan plan
    insStmt = p2_plan.insert()
    result = insStmt.execute(plan_identifier='p2_span_fileupload',
                             so_module='p2.datashackle.management.span.fileupload',
                             so_type='Fileupload')

    # ActionSpan plan
    result = p2_plan.insert().execute(plan_identifier='p2_span_action',
                             so_module='p2.datashackle.management.span.span',
                             so_type='Action')
    action_span_plan_id = result.inserted_primary_key[0]
    
    # Alphanumeric plan
    result = p2_plan.insert().execute(plan_identifier='p2_span_alphanumeric',
                             so_module='p2.datashackle.management.span.alphanumeric',
                             so_type='Alphanumeric')
    
    # Checkbox plan
    result = p2_plan.insert().execute(plan_identifier='p2_span_checkbox',
                             so_module='p2.datashackle.management.span.checkbox',
                             so_type='Checkbox')
    checkbox_span_plan_id = result.inserted_primary_key[0]

    
    # A plan that operates on p2_plan
    result = p2_plan.insert().execute(plan_identifier='p2_plan',
                             so_module='p2.datashackle.management.plan.plan',
                             so_type='Plan')
    
    p2_plan.insert().execute(plan_identifier='p2_countries',
                             so_module='p2.datashackle.core.models.setobject_types',
                             so_type='p2_country')

def downgrade(migrate_engine):
    pass
