# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2010
# Author:  Michael Jenny <michael.jenny%40projekt-und-partner.com>

import copy
import grok
import json
import random

from sqlalchemy import orm
from zope.component import getMultiAdapter, queryMultiAdapter, getUtility
from zope.app.appsetup.interfaces import IDatabaseOpenedWithRootEvent
from zope.catalog.interfaces import ICatalog

from p2.datashackle.core.app.directive import tablename, maporder
from p2.datashackle.core.app.exceptions import *
from p2.datashackle.core.app.setobjectreg import setobject_table_registry
from p2.datashackle.core.interfaces import *
from p2.datashackle.core.models.setobject_types import SetobjectType

class SpanType(SetobjectType):
    grok.implements(ISpanType)
    tablename('p2_span')
    
    label_width = 95
 
    def __init__(self, span_name=None, objid=None):
        super(SpanType, self).__init__(objid)
        # BEGIN sqlalchemy instrumented attributes
        # self.span_identifier initialized through SetobjectType base class.
        self.widget = None
        self.span_name = span_name
        self.span_type = self.__class__.__name__.lower()
        self.visible = True
        # END sqlalchemy instrumented attributes
     
    def common_init(self):
        super(SpanType, self).common_init()
        self.operational = False # Designer mode or user mode?
        self.op_setobject_id = None
        self.op_setobject_type = None
  
    def make_operational(self, setobject):
        self.operational = True
        self.setobject = setobject
        self.op_setobject_id = setobject.id
    
    def onbefore_set_payload_attribute(self, setobject, attribute, value, mode):
        """This method is called when an attribute of this span's payload (a user setobject) is going to be set.
        """   

    def onbefore_post_order_traverse(self, setobject, mode):
        """Called before a span's setobject is travered in post order.
        """    
 
    def lookup_view(self, request, view_mode, relation_linkage_id=None):
        # Check for specialized view class
        view = queryMultiAdapter((self, request), name=self.span_type)
        if view == None:
            # Use the generalized class
            view = getMultiAdapter((self, request), context=self, name="span")
            view.template_name = self.span_type
       
        view.mode = view_mode

        if relation_linkage_id is not None:
            view.relation_linkage_id = relation_linkage_id

        return view
    
    def _get_info(self):
        """This method is intended to be overwritten by subclasses."""
        return {}
    
    def get_info(self):
        info = {'operational': self.operational,
                'module': self.operational and self.op_setobject_type and self.op_setobject_type.__module__ or self.__class__.__module__,
                'type': self.operational and self.op_setobject_type and self.op_setobject_type.__name__ or self.__class__.__name__,
                'data_node_id': self.operational and self.op_setobject_id or self.span_identifier,
                'css_style': self.css_style,
                'span_type': self.span_type,
                'span_name': self.span_name,
                'action': self.operational and self.setobject.action or self.action,
                'span_value': self.span_value,
                'visible': self.visible,
                'span_identifier': self.span_identifier,
                'archetype': self.is_archetype(),
                }
                
        if not self.operational:
            info['attr_name'] = 'span_value'
                
        # Extend the above with type specific info.
        info.update(self._get_info())
        json_info = json.dumps(info)
        return json_info
        
    def is_archetype(self):
        """ Check whether we are on an archetype form """
        return self.widget.is_archetype()
             
    @classmethod
    def map_computed_properties(cls):
        cls.sa_map_dispose()
        table_type = setobject_table_registry.lookup_by_class(SpanType.__module__, SpanType.__name__)

        # Map base class
        #    
        # with_polymorphic="*":  This loads attributes from tables that use
        # joined table inheritance (p2_span_relation) as well.
        # when doing something like query(SpanType).filter(RelationSpan.span_identifier = relation_span_id)
        span_mapper = orm.mapper(
            cls,
            table_type,
            polymorphic_on=table_type.c.span_type,
            polymorphic_identity='spantype',
            properties=cls.mapper_properties,
            with_polymorphic='*', 
       )
    
    
class Action(SpanType):
    maporder(2)
    tablename('p2_span_action')

    @classmethod
    def map_computed_properties(cls):
        cls.sa_map_dispose()
        action_table = setobject_table_registry.lookup_by_class(cls.__module__, cls.__name__)
        inherits = SpanType._sa_class_manager.mapper
        orm.mapper(Action,
                    action_table, # We want joined table inheritance for the action span (additional table for action specific fields)
                    inherits=inherits,
                    polymorphic_identity='action',
                    properties=cls.mapper_properties,
                  )
    
    def _get_info(self):
        info = {}
        info['msg_close'] = self.msg_close
        info['msg_reset'] = self.msg_reset
        return info





