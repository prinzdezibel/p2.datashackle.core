# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2010
# Author:  Michael Jenny <michael.jenny%40projekt-und-partner.com>

import grok

from sqlalchemy import orm, String, Column, Boolean, ForeignKey, Table

from p2.datashackle.core.app.exceptions import *
from p2.datashackle.core.app.setobjectreg import setobject_table_registry, setobject_type_registry
from p2.datashackle.core.sql import select_tables, field_exists
from p2.datashackle.core.globals import metadata
from p2.datashackle.core.models.cardinality import Cardinality
from p2.datashackle.core.models.linkage import Linkage
from p2.datashackle.core.models.relation import Relation
from p2.datashackle.core.models.model import StrippedModel
from p2.datashackle.core.models.model import create_setobject_type


def orm_mapping(event=None):
    # Register table type for grokked ModelBase classes
    registered = []
    for setobject_type in setobject_type_registry.values():
        class_name = setobject_type.__name__
        table_name = setobject_type.get_table_name()
        # Create SA table type
        if setobject_table_registry.get_by_table(table_name) == None:
            table_type = Table(table_name, metadata, autoload=True)
        else:
            table_type = setobject_table_registry.lookup_by_table(table_name)
        # And register it.
        setobject_table_registry.register_type(class_name, table_name, table_type)
        registered.append(class_name)

    # register all the non-grokked, remaining tables (e.g. user tables) 
    register_remaining_tables(registered)
    
    map_tables() 
      
def register_remaining_tables(registered):
    res = select_tables()
    for rec in res:
        table_identifier = str(rec.table)
        class_name = str(rec.klass)
        if not class_name in registered:
            # There's no sa table type for this table yet. Create one and map to a generic ModelBase.
            registered.append(table_identifier)
            # Create SA table type
            table_type = Table(table_identifier, metadata, autoload=True)
            # Register table type
            setobject_table_registry.register_type(class_name, table_identifier, table_type)
            # Create a new setobject orm type
            setobject_type = create_setobject_type(class_name, table_identifier, do_mapping=False)
    res.close()

def map_field_attr(table_name, field_identifier, column_type):
    assert(field_identifier != None)
    if not field_exists(table_name, field_identifier):
        # Create new Field
        new_column = Column(field_identifier, column_type)
        table = setobject_table_registry.lookup_by_table(table_name)
        new_column.create(table)

        # re-map setobject type
        map_tables(exclude_sys_tables=True)

BOOTSTRAP_CLASSES = ('Cardinality', 'Relation', 'StrippedModel', 'Linkage')

def needs_mapping(setobject_type, exclude_sys_tables):
    klass = setobject_type.__name__
    if klass in BOOTSTRAP_CLASSES:
        return False
    table_name = setobject_type.get_table_name()
    if exclude_sys_tables and table_name.startswith('p2_'):
        return False
    return True

def map_tables(exclude_sys_tables=False):
    # Map bootstrap orm Linkage object (and dependent objects 
    # Relation and Cardinality) by hand
    if not exclude_sys_tables:
        for klass in BOOTSTRAP_CLASSES:
            class_ = setobject_type_registry.lookup(klass)
            class_.sa_map()

    # First, create all properties for the orm.relation method. This is a separate step,
    # as we use the sqlalchemy orm query object that requires all mapping acitvies are in a consistent state.
    # This we can only guarantee before and after the mapping process. Therefore we do it before.
    for setobject_type in setobject_type_registry.values():
        if needs_mapping(setobject_type, exclude_sys_tables):
            try:
                setobject_type.compute_mapper_properties()
            except NoPrimaryKeyException:
                # Table has no primary key, don't map it
                table_identifier = setobject_type.get_table_name()
                setobject_type_registry.delete_by_table(table_identifier)
                setobject_table_registry.delete_by_table(table_identifier)
  
    # In a second step we do the actual mapping with the already computed properties 
    # Map table type to ORM setobject type
    for setobject_type in setobject_type_registry.values():
        if needs_mapping(setobject_type, exclude_sys_tables):
            setobject_type.map_computed_properties()

