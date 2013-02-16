# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2010
# Author:  Jonas Thiem <jonas.thiem%40projekt-und-partner.com>

from sqlalchemy import orm, Column, Table, String, Integer
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm.collections import column_mapped_collection
from sqlalchemy.util import OrderedDict
from sqlalchemy.orm.collections import MappedCollection
from zope.component import getUtility

from p2.datashackle.core import model_config, Session
from p2.datashackle.core.app.exceptions import *
from p2.datashackle.core.app.setobjectreg import setobject_type_registry, setobject_table_registry
from p2.datashackle.core.sql import field_exists
from p2.datashackle.core.globals import metadata
from p2.datashackle.core.interfaces import *
from p2.datashackle.core.models.setobject_types import SetobjectType
from p2.datashackle.core.models.relation import Relation


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


@model_config()
class Linkage(SetobjectType):
        
    def __init__(self):
        self.cascade = 'save-update, merge'
        self.post_update = False
        self.back_populates = None
        self.relation = Relation()
        super(Linkage, self).__init__()
   
    @classmethod
    def compute_mapper_properties(cls):
        pass
    
    @classmethod
    def map_computed_properties(cls):
        pass
    
    @classmethod
    def sa_map(cls):
        #cls.sa_map_dispose()
        #cardinality_type.sa_map_dispose()
        #orm.mapper(cardinality_type, cardinality_table)
        Relation = setobject_type_registry.lookup('Relation')
        Model = setobject_type_registry.lookup('Model')
        orm.mapper(cls,
            cls.get_table_class(),
            properties={'relation': orm.relation(
                Relation,
                uselist=False,
                primaryjoin = (Relation.get_table_class().c.id == cls.get_table_class().c.fk_p2_relation)),
            'source_model': orm.relation(Model, uselist=False,
                primaryjoin= (Model.get_table_class().c.plan_identifier == cls.get_table_class().c.fk_source_model)),
            'target_model': orm.relation(Model, uselist=False,
                primaryjoin= (Model.get_table_class().c.plan_identifier == cls.get_table_class().c.fk_target_model))
            }
        )
      
    def compute_orm_properties(self, THIS_IS_A_DIRTY_HACK_PROPERTIES_DICT):
        mappedsotype = setobject_type_registry.lookup(self.target_model.klass)
        xref_table_class = None
        sourcetable = setobject_table_registry.lookup_by_class(self.source_model.klass)
        targettable = setobject_table_registry.lookup_by_class(self.target_model.klass)
        if self.cardinality.id == 'MANY_TO_ONE' or \
                self.cardinality.id == 'ONE(FK)_TO_ONE':
            # take primary key on our side
            primaryfk = getattr(sourcetable.c, self.relation.foreignkeycol)
            primaryidentifier = getattr(targettable.c, mappedsotype.get_primary_key_attr_name())
            primaryjoin = (primaryfk == primaryidentifier)
            secondaryjoin = None
        elif self.cardinality.id == 'ONE_TO_MANY' or \
                self.cardinality.id == 'ONE_TO_ONE(FK)':
            # take primary key on other side
            primaryfk = getattr(targettable.c, self.relation.foreignkeycol)
            primaryidentifier = getattr(
                sourcetable.c,
                setobject_type_registry.lookup(self.source_model.klass).get_primary_key_attr_name()
            )
            primaryjoin = (primaryfk == primaryidentifier)
            secondaryjoin = None
        elif self.cardinality.id == 'MANY_TO_MANY':
            # xref! we actually need two clauses here.
            
            # Obtain table class:
            xref_table_class = setobject_table_registry.get_by_table(self.relation.xref_table)
            if xref_table_class is None:
                # Class is not mapped (probably not having a primary key or something like that) -> autoload
                xref_table_class = Table(self.relation.xref_table, metadata, autoload=True, useexisting=True, autoload_with=getUtility(IDbUtility).engine)
            
            # Compose two join clauses
            primaryjoin = (cls.get_primary_key_column() == getattr(xref_table_class.c, self.relation.foreignkeycol))
            secondaryjoin = (mappedsotype.get_primary_key_column() == getattr(xref_table_class.c, self.relation.foreignkeycol2))
        
        # add the obtained setobject to our mapped properties
        if self.cardinality.id == 'MANY_TO_ONE':
            # This mapping should really not happen here and now.
            # Instead, the linkage MUST be persisted into
            # table p2_linkage at save time!
            THIS_IS_A_DIRTY_HACK_PROPERTIES_DICT[self.attr_name] = orm.relation(
                mappedsotype,
                uselist=False,
                cascade=self.cascade,
                back_populates=self.back_populates,
                primaryjoin=primaryjoin,
                post_update=self.post_update
            )
            relationarguments = {
                'uselist' : False,
                'cascade' : self.cascade,
                'back_populates' : self.back_populates,
                'primaryjoin' : primaryjoin,
                'post_update' : self.post_update
            }
        else:
            # the other side has the foreign key, store things as a collection
            
            order_by = None
            collection_class = None
            
            # This is a special case for the spans as they should not be mapped as ordinary
            # dictionary, but rather as an orderable dictionary. This is necessary to retain the insert order
            # as a ordinary dict isn't ordered. Consider this to be implemented in a more generic way if this
            # use case is occuring for user relations as well.
            if self.attr_name == 'spans' and self.source_model.klass == 'WidgetType':
                collection_class=SpanCollectionClass
                span_table = setobject_table_registry.lookup_by_table('p2_span')
                order_by=span_table.c.order
            
            # This is another special case to ensure the widgets being tab ordered
            if self.attr_name == 'widgets' and self.source_model.klass == 'FormType':
                collection_class = WidgetCollectionClass
                widget_table = setobject_table_registry.lookup_by_table('p2_widget')
                order_by=widget_table.c.tab_order
            
            # Get collection class
            if collection_class == None:
                if self.ref_key is None:
                    collection_class = column_mapped_collection(mappedsotype.get_primary_key_column())
                else:
                    mapped_column = mappedsotype.get_column(self.ref_key)
                    collection_class = column_mapped_collection(mapped_column)
            
            # Compute arguments:
            relationarguments = {
                'back_populates' : self.back_populates,
                'collection_class' : collection_class,
                'uselist' : True,
                'primaryjoin': primaryjoin,
                'cascade' : self.cascade,
                'post_update' : self.post_update
                }
            if order_by is not None:
                relationarguments['order_by'] = order_by
        
        # Set xref table if we got one
        if xref_table_class is not None:
            relationarguments['secondary'] = xref_table_class
            if secondaryjoin is not None:
                relationarguments['secondaryjoin'] = secondaryjoin
        
        return relationarguments

    @property
    def cardinality(self):
        return self.relation.cardinality

    @property
    def use_list(self):
        if self.relation.cardinality.id == 'ONE_TO_MANY' or \
                self.relation.cardinality.id == 'MANY_TO_MANY':
            return True
        else:
            return False
    
    #@orm.reconstructor 
    #def reconstruct(self):
    #    super(Linkage, self).reconstruct()
    
    #@property
    #def shareable(self):
    #    if self.cardinality is not None:
    #        if self.cardinality.cardinality == '1:1(fk)' or self.relation.cardinality.cardinality == '1(fk):1':
    #            return False
    #    return True
      
    ## TODO: move to Relation 
    #def check_relation_value(self, attribute):
    #    value = getattr(self.relation, attribute)
    #    if value is not None:
    #        if len(value) > 0:
    #            return True
    #    raise UserException("Linkage attribute '" + attribute + "' is not specified.")
    #
    #def check_value(self, attribute):
    #    value = getattr(self, attribute)
    #    if value is not None:
    #        if len(value) > 0:
    #            return True
    #    raise UserException("Linkage attribute '" + attribute + "' is not specified.")
    #

    #def _validate_many_to_many(self):

    #    if self.relation.xref_table is None or len(self.relation.xref_table) <= 0 or \
    #            self.relation.foreignkeycol2 is None or len(self.relation.foreignkeycol2) <= 0:
    #        raise UserException("You must specify a second foreign key column and an xref table name")
    #    
    #    self.check_relation_value("foreignkeycol2")
    #    self.check_relation_value('xref_table')
    #    self.check_value("source_module")
    #    self.check_value("source_classname")
    #    self.check_value("target_module")
    #    self.check_value("target_classname")
    #    self.check_value("attr_name")
    #    self.check_relation_value("foreignkeycol")

    #def _validate_many_to_one(self):
    #    """Validation for MANY_TO_ONE and
    #    ONE(FK)_TO_MANY use cases.
    #    """
    #    # MANY_TO_ONE and ONE(FK)_TO_ONE related initialization
    #    
    #    self.check_value("source_module")
    #    self.check_value("source_classname")
    #    self.check_value("target_module")
    #    self.check_value("target_classname")
    #    self.check_value("attr_name")
    #    self.check_relation_value("foreignkeycol")

    #def _validate_one_to_many(self):
    #    self.check_value("source_module")
    #    self.check_value("source_classname")
    #    self.check_value("target_module")
    #    self.check_value("target_classname")
    #    self.check_value("attr_name")
    #    self.check_relation.value("foreignkeycol")

           
    #def common_init(self):
    #    super(Linkage, self).common_init()
    #    self.compute_cardinality()
        
    #def _foreign_key_is_on_target_side(self):
    #    """ Just checks if the foreign key is on the 'target' side or not (n:m will also count as 'not').
    #        Returns True or False accordingly."""
    #    if self.relation.cardinality is None:
    #        raise UserException("No cardinality specified")
    #    cardinalitystr = self.relation.cardinality.cardinality
    #    if cardinalitystr.endswith(":n") or cardinalitystr.endswith(":1(fk)"):
    #        return True
    #    return False
    #    
    #def cardinality_list(self):
    #    if self.relation.cardinality is None:
    #        return None
    #    # Obtain cardinality string value:
    #    cardinalitystr = self.relation.cardinality.cardinality
    #    # Split it up into a list:
    #    cardinalitylist = cardinalitystr.replace('1(fk)', '1').replace('n', '-1').replace('m','-1').split(':', 2)
    #    if len(cardinalitylist) != 2:
    #        return
    #    # A short consistency check:
    #    i = 0
    #    while i < 2:
    #        try:
    #            cardinalitylist[i] = int(cardinalitylist[i])
    #        except:
    #            raise Exception("Invalid cardinality value")
    #        if cardinalitylist[i] < 1 and cardinalitylist[i] != -1:
    #            raise Exception("Invalid cardinality value")
    #        i += 1
    #    return cardinalitylist

    #def compute_cardinality(self):
    #    if self.relation.cardinality is not None:
    #        cardinality = self.cardinality_list()
    #        if not cardinality:
    #            return
    #        self.source_cardinality = cardinality[0]
    #        self.target_cardinality = cardinality[1]
    #        

    #def is_foreignkey_on_target_table(self):
    #    """ Checks if the foreign key is on the target table, relative from the source table
    #        from where this linkage originates.
    #        Returns either True, False or a string "xref" for n:m relations. """
    #    self.compute_cardinality()
    #    if self.source_cardinality != 1 and self.target_cardinality != 1:
    #        return "xref"
    #    if self._foreign_key_is_on_target_side() == True:
    #        return True
    #    return False
    
