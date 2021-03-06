# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2010
# Author:  Michael Jenny <michael.jenny%40projekt-und-partner.com>

import grok

from migrate.changeset import *
from p2.datashackle.core.globals import metadata
from p2.datashackle.core.app.exceptions import *
from p2.datashackle.core.app.setobjectreg import setobject_table_registry, setobject_type_registry
from p2.datashackle.core.interfaces import IDbUtility
from p2.datashackle.core.models.identity import generate_random_identifier
from sqlalchemy import orm, String, Boolean, ForeignKey, or_
from sqlalchemy.sql import select, and_
from sqlalchemy.orm import mapper, object_mapper, object_session
from sqlalchemy.orm.exc import UnmappedClassError
from sqlalchemy.orm.mapper import _mapper_registry
from sqlalchemy.orm.util import has_identity
from sqlalchemy import and_
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.properties import RelationshipProperty
from zope.component import getUtility, Interface


class classproperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


def create_basemodel_type(class_name, table_name, do_mapping=True):
    """Create a setobject derived ORM type at runtime."""

    # The third parameter of builtin function 'type' is a dictionary which becomes the class' __dict__. We define the __init__
    # function that gets called whenever the setobject type is instantiated and its purpose is to call the
    # base class' (ModelBase) __init__ function.
    setobject_type = type(class_name, (ModelBase, ), {'__init__': lambda x: super(setobject_type, x).__init__()})

    setobject_type.table_name = table_name

    # Register setobject class type
    setobject_type_registry.register_type(setobject_type, 1)

    # map class to table
    if do_mapping == True:
        # deferred import
        from p2.datashackle.core.models.mapping import map_tables
        map_tables(exclude_sys_tables=True)

    return setobject_type


class ModelBase(object):
    """ORM base class for all sqlalchemy mapped tables.
    """

    # Linkage contains all linkages of the setobject's type, but NOT the linkages
    # of base classes,from which setobject might be derived from. If interested in
    # all linkages of an object (inclusive the base class linkages) use setobject.collections['attr_name']['linkage']
    # instead.
    linkages = dict()

    def __init__(self):
        if not self.id:
            self.id = generate_random_identifier()
        self.action = 'new'
        self.common_init()

    @orm.reconstructor
    def reconstruct(self):
        if getattr(self, self.get_primary_key_attr_name()) == None:
            raise Exception("No primary key set. Check for data corruption in db (e.g. no record "
                " in derived table for polymorphic object).")
        self.action = "save"
        self.common_init()


    def common_init(self):
        self.collections = {}
        self.link(self.__class__)
        self.walk_bases(self.__class__)
        #pk_keys = set([c.key for c in class_mapper(self.__class__).primary_key])
        #relations = [p for p in class_mapper(self.__class__).iterate_properties
        #                if p.key not in pk_keys and
        #                   p.__class__ == RelationshipProperty]
        #
        #for relation in relations:
        #    from p2.datashackle.core.models.linkage import Linkage
        #    from p2.datashackle.core.models.model import Model
        #    linkage = getUtility(IDbUtility).Session().query(Linkage).join(
        #        (Model, Model.plan_identifier==Linkage.fk_source_model)).filter(
        #        and_(Model.klass == self.__class__.__name__, Linkage.attr_name == relation.key)).one()
        #    self.collections[relation.key] = {
        #        'collection_id': generate_random_identifier(),
        #        'linkage': linkage}

    def link(self, klass):
        klass.fetch_linkages()
        for linkage in klass.linkages.itervalues():
            self.collections[linkage.attr_name] = {
                'collection_id': generate_random_identifier(),
                'linkage': linkage}


    def walk_bases(self, cls):
        for base_class in cls.__bases__:
            if issubclass(base_class, ModelBase) and base_class != ModelBase:
                self.walk_bases(base_class)
                self.link(base_class)

    def get_object_state(self):
        if object_session(self) is None and not has_identity(self):
            return 'transient'
        elif object_session(self) is not None and not has_identity(self):
            return 'pending'
        elif object_session(self) is None and has_identity(self):
            return 'detached'
        elif object_session(self) is not None and has_identity(self):
            return 'persistent'
        raise Exception

    def set_attribute(self, attribute, value, mode):
        setattr(self, attribute, value)

    def pre_order_traverse(self):
        pass

    def post_order_traverse(self, mode):
        pass

    def generate_identifier(self):
        """Generates a identifier for the setobject. It is at the moment a random identifier, but probably there should later
        be a more deterministic way of doing that.
        """
        return generate_random_identifier()

    @classmethod
    def get_primary_key_column(cls):
        """Returns the name of the mapped primarykey column."""
        column_set = cls.get_table_class().primary_key.columns
        if len(column_set) != 1:
            raise NoPrimaryKeyException(cls.get_table_name(), "Either there is no primary key or it is a composite one. Can't work with that.")
        column = column_set[cls.get_table_class().primary_key.columns.keys()[0]]
        return column

    @classmethod
    def get_column(cls, name):
        """Returns a column by name"""
        table_type = setobject_table_registry.lookup_by_class(cls.__name__)
        return getattr(table_type.c, name)

    @classmethod
    def get_primary_key_attr_name(cls):
        return cls.get_primary_key_column().name

    @classmethod
    def get_primary_key_attr(cls):
        """Returns the python attribute that holds the id (See 'id' property)."""
        return getattr(cls, cls.get_primary_key_attr_name())

    @classmethod
    def get_table_name(cls):
        return cls.table_name

    @classmethod
    def get_table_class(cls):
        return setobject_table_registry.lookup_by_table(cls.get_table_name())

    # Provide a class method property to get table class
    # http://stackoverflow.com/questions/128573/using-property-on-classmethods
    table = classproperty(get_table_class)

    def _get_id(self):
        """Returns the value of the setobject instance's mapped primarykey column."""
        pk_attr_name = self.get_primary_key_attr_name()
        return getattr(self, pk_attr_name)

    def set_id(self, value):
        setattr(self, self.get_primary_key_attr_name(), value)

    id = property(_get_id, set_id)

    @classmethod
    def sa_map_dispose(cls):
        if hasattr(cls, "_sa_class_manager"):
            try:
                cls._sa_class_manager.mapper.dispose()
            except UnmappedClassError:
                pass

    @classmethod
    def map_computed_properties(cls):
        cls.sa_map_dispose()
        table_name = cls.get_table_name()
        table_type = setobject_table_registry.lookup_by_table(table_name)
        if not hasattr(cls, 'mapper_properties'):
            raise Exception("Can't map without mapping properties. Ensure that they are " \
                "created beforehand with compute_mapper_properties."
                )
        orm.mapper(cls,
                  table_type,
                  properties=cls.mapper_properties,
                  )

    @classmethod
    def sa_map(cls):
        cls.compute_mapper_properties()
        cls.map_computed_properties()

    @classmethod
    def fetch_linkages(cls):
        # deferred imports
        from p2.datashackle.core.models.linkage import Linkage

        linkagelist = getUtility(IDbUtility).Session().query(Linkage).join(
            (StrippedModel, StrippedModel.plan_identifier==Linkage.fk_source_model)).filter(
            StrippedModel.klass == cls.__name__).all()
        cls.linkages = dict()
        for linkage in linkagelist:
             cls.linkages[linkage.attr_name] = linkage

    @classmethod
    def compute_mapper_properties(cls):
        cls.get_primary_key_column() # make sure we have one! (will throw exception if that is not the case)
        properties = {}
        cls.fetch_linkages()
        for linkage in cls.linkages.itervalues():
            mappedsotype = setobject_type_registry.lookup(
                linkage.target_model.klass)

            if linkage.cardinality.id != 'NONE':
                # TODO: Don't pass properties. This is a nasty hack!
                mapper_properties = linkage.compute_orm_properties(properties)
                properties[linkage.attr_name] = orm.relation(mappedsotype, **mapper_properties)

        cls.mapper_properties = properties

from p2.datashackle.core import model_config

@model_config()
class StrippedModel(ModelBase):
    """Operates like Plan on p2_model without the need to import the Plan class type.
        It has the same instrumented attributes like Plan.
    """
    @classmethod
    def sa_map(cls):
        orm.mapper(cls, cls.get_table_class())

