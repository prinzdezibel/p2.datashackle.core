# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2010
# Author:  Michael Jenny <michael.jenny%40projekt-und-partner.com>

import logging
import grok
import random
import traceback

from migrate.changeset import *
from sqlalchemy import orm, String, Boolean, ForeignKey, or_
from sqlalchemy.orm import mapper, object_mapper
from sqlalchemy.sql import and_
from sqlalchemy.orm.mapper import _mapper_registry
from sqlalchemy.orm.collections import column_mapped_collection
from sqlalchemy.orm.exc import UnmappedClassError
from sqlalchemy.orm import object_session 
from sqlalchemy.orm.util import has_identity 
from zope.component import getUtility, Interface

from p2.datashackle.core.globals import metadata
from p2.datashackle.core.app.directive import tablename, maporder
from p2.datashackle.core.app.exceptions import *
from p2.datashackle.core.app.setobjectreg import setobject_table_registry, setobject_type_registry
from p2.datashackle.core.interfaces import IDbUtility
from p2.datashackle.core.models.identity import generate_random_identifier
from p2.datashackle.core.models.table import Table

from sqlalchemy.util import OrderedDict
from sqlalchemy.orm.collections import MappedCollection



class SpanCollectionClass(OrderedDict, MappedCollection):
    """Holds span objects, keyed by the 'span_name' attribute with insert order maintained."""

    def __init__(self, *args, **kw):
        MappedCollection.__init__(self, keyfunc=lambda span: span.span_name)
        OrderedDict.__init__(self, *args, **kw)
        
class WidgetCollectionClass(OrderedDict, MappedCollection):
    """Holds span objects, keyed by the 'span_name' attribute with insert order maintained."""

    def __init__(self, *args, **kw):
        MappedCollection.__init__(self, keyfunc=lambda widget: widget.widget_identifier)
        OrderedDict.__init__(self, *args, **kw)


def create_setobject_type(table_name, do_mapping=True):
    """Create a setobject derived ORM type at runtime."""
    
    # The third parameter of builtin function 'type' is a dictionary which becomes the class' __dict__. We define the __init__
    # function that gets called whenever the setobject type is instantiated and its purpose is to call the
    # base class' (SetobjectType) __init__ function.
    setobject_type = type(table_name, (SetobjectType, ), {'__init__': lambda x, objid=None: super(setobject_type, x).__init__(objid)})

    # Set tablename directive for newly created setobject type class
    tablename.set(setobject_type, table_name)

    # Register setobject class type
    setobject_type_registry.register_type(setobject_type, 1)
      
    # map class to table
    if do_mapping == True:
        # deferred import
        from p2.datashackle.core.models.mapping import map_tables
        map_tables(exclude_sys_tables=True)
    
    return setobject_type
     
   
class SetobjectType(object):
    """ORM base class for all sqlalchemy mapped tables. Setobjects are instances of derived classes from this class."""

    # Linkage contains all linkages of the setobject's type, but NOT the linkages
    # of base classes,from which setobject might be derived from. If interested in
    # all linkages of an object (inclusive the base class linkages) use setobject.collections['attr_name']['linkage']
    # instead.
    linkages = dict()  

    def __init__(self, objid=None):
        if objid != None and len(objid) == 0:
            raise UnspecificException("The object id must not be empty.")
        setattr(self, self.get_primary_key_attr_name(), objid if objid != None else generate_random_identifier())
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
        def link(class_):
            class_.compute_linkages()
            for linkage in class_.linkages.itervalues():
                self.collections[linkage.attr_name] = {
                    'collection_id': generate_random_identifier(),
                    'linkage': linkage,
                    }

        self.collections = {}
        link(self.__class__)
        for base_class in self.__class__.__bases__:
            if issubclass(base_class, SetobjectType) and base_class != SetobjectType:
                link(base_class)
    
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
        table_type = setobject_table_registry.lookup_by_class(cls.__module__, cls.__name__)
        return getattr(table_type.c, name)
   
    @classmethod
    def get_primary_key_attr_name(cls):
        column = cls.get_primary_key_column()
        return column.name
                
    @classmethod
    def get_primary_key_attr(cls):
        """Returns the python attribute that holds the id (See 'id' property)."""
        return getattr(cls, cls.get_primary_key_attr_name())    
        
    @classmethod
    def get_table_name(cls):
        table_name = tablename.bind().get(cls)
        if not table_name:
            raise Exception("No table name specified. Please use the tablename directive to specify the table name "
                            "for class %r" % cls)
        return table_name
    
    @classmethod
    def get_table_class(cls):
        return setobject_table_registry.lookup_by_table(cls.get_table_name())
 
    def _get_id(self):
        """Returns the value of the setobject instance's mapped primarykey column."""
        pk_attr_name = self.get_primary_key_attr_name()
        return getattr(self, pk_attr_name)

    def _set_id(self, value):
        setattr(self, self.get_primary_key_attr_name(), value)

    id = property(_get_id, _set_id)

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
    def compute_linkages(cls):
        cls.linkages = {}
        
        # get all linkages associated with ourselves
        from p2.datashackle.core.models.linkage import Linkage
        linkagelist = getUtility(IDbUtility).Session().query(Linkage).filter(
            and_(Linkage.source_module == cls.__module__, 
            Linkage.source_classname == cls.__name__)
        ).all()

        # reinitialize linkages
        cls.linkages = dict()
        for linkage in linkagelist:
            cls.linkages[linkage.attr_name] = linkage
                
    @classmethod
    def compute_mapper_properties(cls):
        cls.get_primary_key_column() # make sure we have one! (will throw exception if that is not the case)
        
        table_identifier = cls.get_table_name()
      
        properties = {}
 
        cls.compute_linkages()

        # reinitialize linkages
        for linkage in cls.linkages.itervalues():
            mappedsotype = setobject_type_registry.lookup(linkage.target_module, linkage.target_classname)
            xref_table_class = None
            
            # Generate primary join clause
            sourcetable = setobject_table_registry.lookup_by_class(linkage.source_module, linkage.source_classname)
            targettable = setobject_table_registry.lookup_by_class(linkage.target_module, linkage.target_classname)
            linkage.compute_cardinality()
            if linkage.target_cardinality == 1 or linkage.source_cardinality == 1:
                # 1:n (or n:1) relation
                if linkage.is_foreignkey_on_target_table() != True:
                    # take primary key on our side
                    primaryfk = getattr(sourcetable.c, linkage.foreignkeycol)
                    primaryidentifier = getattr(targettable.c, mappedsotype.get_primary_key_attr_name())
                else:
                    # take primary key on other side
                    primaryfk = getattr(targettable.c, linkage.foreignkeycol)
                    primaryidentifier = getattr(
                        sourcetable.c,
                        setobject_type_registry.lookup(linkage.source_module, linkage.source_classname).get_primary_key_attr_name()
                    )
                primaryjoin = (primaryfk == primaryidentifier)
                secondaryjoin = None
            else:
                # xref! we actually need two clauses here.
                
                # Obtain table class:
                xref_table_class = setobject_table_registry.get_by_table(linkage.xref_table)
                if xref_table_class is None:
                    # Class is not mapped (probably not having a primary key or something like that) -> autoload
                    xref_table_class = Table(linkage.xref_table, metadata, autoload=True, useexisting=True, autoload_with=getUtility(IDbUtility).engine)
                
                # Compose two join clauses
                primaryjoin = (cls.get_primary_key_column() == getattr(xref_table_class.c, linkage.foreignkeycol))
                secondaryjoin = (mappedsotype.get_primary_key_column() == getattr(xref_table_class.c, linkage.foreignkeycol2))
            
            # add the obtained setobject to our mapped properties
            if linkage.ref_type == 'object':
                properties[linkage.attr_name] = orm.relation(mappedsotype,
                    uselist=False,
                    cascade=linkage.cascade,
                    back_populates=linkage.back_populates,
                    primaryjoin=primaryjoin,
                    post_update=linkage.post_update
                )
                relationarguments = {
                    'uselist' : False,
                    'cascade' : linkage.cascade,
                    'back_populates' : linkage.back_populates,
                    'primaryjoin' : primaryjoin,
                    'post_update' : linkage.post_update
                }
            else:
                # the other side has the foreign key, store things as a collection
                
                order_by = None
                collection_class = None
                
                # This is a special case for the spans as they should not be mapped as ordinary
                # dictionary, but rather as an orderable dictionary. This is necessary to retain the insert order
                # as a ordinary dict isn't ordered. Consider this to be implemented in a more generic way if this
                # use case is occuring for user relations as well.
                if linkage.attr_name == 'spans' and linkage.source_classname == 'WidgetType':
                    collection_class=SpanCollectionClass
                    span_table = setobject_table_registry.lookup_by_table('p2_span')
                    order_by=span_table.c.order
                
                # This is another special case to ensure the widgets being tab ordered
                if linkage.attr_name == 'widgets' and linkage.source_classname == 'FormType':
                    collection_class = WidgetCollectionClass
                    widget_table = setobject_table_registry.lookup_by_table('p2_widget')
                    order_by=widget_table.c.tab_order
                
                # Get collection class
                if collection_class == None:
                    if linkage.ref_key is None:
                        collection_class = column_mapped_collection(mappedsotype.get_primary_key_column())
                    else:
                        mapped_column = mappedsotype.get_column(linkage.ref_key)
                        collection_class = column_mapped_collection(mapped_column)
                
                # Compute arguments:
                relationarguments = {
                    'back_populates' : linkage.back_populates,
                    'collection_class' : collection_class,
                    'uselist' : True,
                    'primaryjoin' :primaryjoin,
                    'cascade' : linkage.cascade,
                    'post_update' : linkage.post_update
                    }
                if order_by is not None:
                    relationarguments['order_by'] = order_by
            
            # Set xref table if we got one
            if xref_table_class is not None:
                relationarguments['secondary'] = xref_table_class
                if secondaryjoin is not None:
                    relationarguments['secondaryjoin'] = secondaryjoin
                
            # Set the relation with the given arguments   
            properties[linkage.attr_name] = orm.relation(mappedsotype, **relationarguments)
            
        cls.mapper_properties = properties

