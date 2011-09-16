# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2010
# Author:  Michael Jenny <michael.jenny%40projekt-und-partner.com>

import random

from sqlalchemy import *
from migrate import *
from migrate.changeset import *
from migrate.changeset.constraint import ForeignKeyConstraint


class upgradedataobj(object):

    def generate_random_identifier(self):
        n_id = random.randint(0, 100000000)
        id = "%08d" % n_id
        return id

metadata = MetaData()

p2_plan = Table('p2_plan',
                metadata,
                Column('plan_identifier', String(length=255), primary_key=True, nullable=False, autoincrement=False),
                Column('fk_default_form', String(8), index=True),
                Column('so_module', String(255), nullable=False),
                Column('so_type', String(255), nullable=False),
                mysql_engine='InnoDB',
                )

p2_form = Table('p2_form',
                metadata,
                Column('form_identifier', String(8), primary_key=True, autoincrement=False),
                Column('width', SmallInteger, nullable=True),
                Column('height', SmallInteger, nullable=True),
                Column('form_name', String(63)),
                Column('fk_p2_plan', ForeignKey('p2_plan.plan_identifier'), nullable=True),
                mysql_engine='InnoDB',
                )

p2_widget = Table('p2_widget',
                metadata,
                Column('widget_identifier', String(8), primary_key=True, autoincrement=False),
                Column('fk_p2_form', ForeignKey('p2_form.form_identifier')),
                Column('widget_type', String(63), nullable=False),
                Column('css_style', String(255), nullable=True, default=''),
                Column('tab_order', Integer, nullable=False, default=0),
                mysql_engine='InnoDB',
                )

p2_cardinality = Table('p2_cardinality',
   metadata,
   Column('id', String(length=8), primary_key=True, nullable=False, autoincrement=False),
   Column('cardinality', String(64), nullable=False),
   mysql_engine='InnoDB',
)

p2_linkage = Table('p2_linkage',
             metadata,
             Column('id', String(8), primary_key=True, autoincrement=False),
             Column('attr_name', String(63), nullable=True),
             Column('ref_type', String(63), nullable=False),
             Column('ref_key', String(63), nullable=True),
             Column('foreignkeycol', String(63), nullable=True),
             Column('foreignkeycol2', String(63), nullable=True), # Required for n:m relations
             Column('source_module', String(255), nullable=True),
             Column('source_classname', String(255), nullable=True),
             Column('target_module', String(255), nullable=True),
             Column('target_classname', String(255), nullable=True),
             Column('xref_table', String(255), nullable=True),
             Column('back_populates', String(63), nullable=True),
             Column('cascade', String(255), nullable=True),
             Column('fk_cardinality', ForeignKey('p2_cardinality.id'), nullable=True),
             Column('post_update', Boolean), #http://www.sqlalchemy.org/docs/05/mappers.html#rows-that-point-to-themselves-mutually-dependent-rows
             mysql_engine='InnoDB')


p2_span = Table('p2_span',
            metadata,
            Column('span_identifier', String(8)),
            Column('fk_p2_widget', ForeignKey('p2_widget.widget_identifier')),
            Column('span_name', String(63), index=True),
            Column('span_type', String(63), nullable=False),
            Column('span_value', String(255), nullable=True),
            Column('css_style', String(255), nullable=True, default=''),
            Column('visible', Boolean, nullable=True, default=True),
            Column('order', Integer, primary_key=True, autoincrement=True), # Primary key is only temporarily. We are interested in the autoincrement functionality. See below.
            mysql_engine='InnoDB',
            )
# HACK: We want an autoincrementing order field. This allows the spans to retain the insert order.
# http://stackoverflow.com/questions/2937229/set-auto-increment-using-sqlalchemy-with-mysql-on-columns-with-non-primary-keys/5410205#5410205
from sqlalchemy.schema import DDL
DDL("ALTER TABLE p2_span DROP PRIMARY KEY, ADD UNIQUE KEY(`order`); ALTER TABLE p2_span ADD PRIMARY KEY(`span_identifier`);", on='mysql').execute_at('after-create', p2_span)



# This table inherits all attributes from p2_span!
p2_span_alphanumeric = Table('p2_span_alphanumeric',
                 metadata,
                 Column('span_identifier', String(8), ForeignKey('p2_span.span_identifier', onupdate="CASCADE"), primary_key=True), # Joined table inheritance!
                 Column('attr_name', String(63), nullable=True),
                 Column('field_identifier', String(63), nullable=True),
                 Column('multi_line', Boolean, nullable=True),
                 Column('fk_field_type', ForeignKey('p2_fieldtype.id'), nullable=True),
                 Column('required', Boolean, nullable=True, default=True),
                 mysql_engine='InnoDB'
                 )

# This table inherits all attributes from p2_span!
p2_span_checkbox = Table('p2_span_checkbox',
                 metadata,
                 Column('span_identifier', String(8), ForeignKey('p2_span.span_identifier', onupdate="CASCADE"), primary_key=True), # Joined table inheritance!
                 Column('attr_name', String(63), nullable=True),
                 Column('field_identifier', String(63), nullable=True),
                 mysql_engine='InnoDB'
                 )

# This table inherits all attributes from p2_span!
p2_span_dropdown = Table('p2_span_dropdown',
                 metadata,
                 Column('span_identifier', String(8), ForeignKey('p2_span.span_identifier', onupdate="CASCADE"), primary_key=True),
                 Column('fk_p2_linkage', ForeignKey('p2_linkage.id', onupdate="CASCADE")),
                 Column('plan_identifier', String(63), nullable=True),
                 Column('attr_name', String(63), nullable=True),
                 Column('required', Boolean, nullable=True, default=False),
                 mysql_engine='InnoDB'
                 )

# This table inherits all attributes from p2_span!
p2_span_relation = Table('p2_span_relation',
                 metadata,
                 Column('span_identifier', String(8), ForeignKey('p2_span.span_identifier', onupdate="CASCADE"), primary_key=True),
                 Column('fk_p2_linkage', ForeignKey('p2_linkage.id', onupdate="CASCADE")),
                 Column('form_name', String(63), nullable=True),
                 Column('plan_identifier', String(63), nullable=True),
                 Column('filter_clause', String(255), nullable=True),
                 Column('editable', Boolean, default=True),
                 mysql_engine='InnoDB'
                 )

# This table inherits all attributes from p2_span!
p2_span_fileupload = Table('p2_span_fileupload',
                 metadata,
                 Column('span_identifier', String(8), ForeignKey('p2_span.span_identifier', onupdate="CASCADE"), primary_key=True), # Joined table inheritance!
                 Column('fk_p2_linkage', ForeignKey('p2_linkage.id', onupdate="CASCADE")),
                 mysql_engine='InnoDB'
                 )

# This table inherits all attributes from p2_span!
p2_span_action = Table('p2_span_action',
                 metadata,
                 Column('span_identifier', String(8), ForeignKey('p2_span.span_identifier', onupdate="CASCADE"), primary_key=True), # Joined table inheritance!
                 Column('msg_reset', Boolean, nullable=False, default=0),
                 Column('msg_close', Boolean, nullable=False, default=0),
                 mysql_engine='InnoDB'
                 )

p2_archetype = Table('p2_archetype',
                         metadata,
                         Column('id', String(8), primary_key=True, autoincrement=False),
                         mysql_engine='InnoDB'
                         )

p2_media = Table('p2_media',
                  metadata,
                  Column('id', String(8), primary_key=True, autoincrement=True),
                  Column('filename', String(255), nullable=True),
                  Column('size', Integer, nullable=True),
                  Column('data', BLOB(16777215)),
                  Column('thumbnail', BLOB),
                  Column('mime_type', String(63)),
                  mysql_engine='InnoDB'
                 )

p2_fieldtype = Table('p2_fieldtype',
   metadata,
   Column('id', String(length=8), primary_key=True, nullable=False, autoincrement=False),
   Column('field_type', String(32), nullable=False),
   mysql_engine='InnoDB',
)

p2_test = Table('test',
                metadata,
                Column('id', String(8), primary_key=True, autoincrement=False),
                mysql_engine='InnoDB'
                )

                                
def upgrade(migrate_engine):
    # Upgrade operations go here.
    metadata.bind = migrate_engine
    
    metadata.create_all()

    ForeignKeyConstraint(columns=[p2_plan.c.fk_default_form]  , refcolumns=[p2_form.c.form_identifier]).create()
    

    
def downgrade(migrate_engine):
    metadata.bind = migrate_engine 
    ForeignKeyConstraint(columns=[p2_plan.c.fk_default_form]  , refcolumns=[p2_form.c.form_identifier]).drop()
    
    # Operations to reverse the above upgrade go here.
    p2_span_dropdown.drop(migrate_engine)
    p2_span_checkbox.drop(migrate_engine)
    p2_span_alphanumeric.drop(migrate_engine)
    p2_span_action.drop(migrate_engine)
    p2_span_fileupload.drop(migrate_engine)
    p2_span_relation.drop(migrate_engine)
    p2_span.drop(migrate_engine)
    p2_linkage.drop(migrate_engine)
    p2_archetype.drop(migrate_engine)
    p2_widget.drop(migrate_engine)
    p2_form.drop(migrate_engine)
    p2_plan.drop(migrate_engine)
    p2_fieldtype.drop(migrate_engine)
    p2_test.drop(migrate_engine)
    p2_cardinality.drop()
