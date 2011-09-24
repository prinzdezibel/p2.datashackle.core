# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2010
# Author:  Michael Jenny <michael.jenny%40projekt-und-partner.com>

import copy
import grok
import json

from grokcore.content import interfaces
from sqlalchemy import orm
from sqlalchemy.sql import and_, or_
from zope.component import getUtility, getMultiAdapter, queryMultiAdapter
from zope.location.interfaces import ILocation

from p2.datashackle.core.interfaces import IWidgetType
from p2.datashackle.core import model_config
from p2.datashackle.core.app.exceptions import UnspecificException
from p2.datashackle.core.app.setobjectreg import setobject_table_registry, setobject_type_registry
from p2.datashackle.core.models.setobject_types import SetobjectType
from p2.datashackle.core.models.span.span_factory import create_span
from p2.datashackle.core.models.identity import generate_random_identifier


@model_config(tablename='p2_widget')
class WidgetType(SetobjectType):
    grok.implements(IWidgetType, interfaces.IContext, ILocation)
    
    js_widget_constructor = 'p2.Widget'
    js_propertyform_constructor = 'p2.PropertyForm'
    
    def __init__(self, objid=None):
        super(WidgetType, self).__init__(objid)
        self.spans = dict()
        self.css_style = ''
        self.tab_order = 0
        self.widget_type = self.__class__.__name__.lower()

    @orm.reconstructor 
    def reconstruct(self):
        super(WidgetType, self).reconstruct()
        self.pre_order_traverse()

    def common_init(self):
        super(WidgetType, self).common_init()
        self.operational = False

    def pre_order_traverse(self):
        if self.form == None:
            raise Exception("Can't finish initialization without the form attribute set.")
        # Make locatable
        self.__parent__ = self.form
        self.__name__ = self.id
        # set op_setobject_type from parent form's attributes
        self.op_setobject_type = setobject_type_registry.lookup(self.form.so_module, self.form.so_type)
        
        for span in self.spans.itervalues():
            span.widget = self
            span.op_setobject_type = self.op_setobject_type

    def make_operational(self, setobject):
        """Makes the widget operational, e.g. (potentially working on a user table via piggybacking spans)."""
        self.operational = True
        self.setobject = setobject
        self.op_setobject_id = setobject.id
        for (key, value) in self.spans.iteritems():
            self.spans[key].make_operational(setobject)
      
    def register_span(self, span_type, span_name, span_identifier=None):
        if not span_name in self.spans:
            self.spans[span_name] = create_span(span_type, span_name, span_identifier)
            self.spans[span_name].widget = self
        return self.spans[span_name]
        
    def lookup_view(self, request, view_mode, relation_linkage_id=None):
        # Check for specialized view class
        view = queryMultiAdapter((self, request), name=self.widget_type)
        if view == None:
            # Use the generalized class
            view = getMultiAdapter((self, request),
                                   name="widget")
            view.template_name = self.widget_type

        view.mode = view_mode         
   
        if relation_linkage_id is not None:
            view.relation_linkage_id = relation_linkage_id
        return view
    
    def is_archetype(self):
        """ Check whether we are on an archetype form """
        return self.form.is_archetype()
        
    @classmethod
    def map_computed_properties(cls):
        cls.sa_map_dispose()
        p2_widget = setobject_table_registry.lookup_by_class(WidgetType.__module__, WidgetType.__name__)    
        # Map base class
        widget_mapper = orm.mapper(
            WidgetType,
            p2_widget,
            polymorphic_on=p2_widget.c.widget_type, polymorphic_identity='widgettype',
            properties=WidgetType.mapper_properties
            )
           
@model_config(tablename='p2_widget', maporder=2)
class Action(WidgetType):
    grok.implements(IWidgetType)   
     
    def __init__(self, objid=None):
        super(Action, self).__init__(objid)
        self.register_span(span_type='action', span_name='button')

    @classmethod
    def map_computed_properties(cls):
        cls.sa_map_dispose()
        inherits = WidgetType._sa_class_manager.mapper
        orm.mapper(Action,
            inherits=inherits,
            polymorphic_identity='action',
            properties=Action.mapper_properties,
            )

   
@model_config(tablename='p2_widget', maporder=2)
class Checkbox(WidgetType):
    grok.implements(IWidgetType)   
 
    def __init__(self, objid=None):
        super(Checkbox, self).__init__(objid)
        self.register_span('label', 'label')
        self.register_span('checkbox', 'piggyback')

    @classmethod
    def map_computed_properties(cls):
        cls.sa_map_dispose()
        inherits = WidgetType._sa_class_manager.mapper
        orm.mapper(Checkbox,
              inherits=inherits,
              polymorphic_identity='checkbox',
              properties=Checkbox.mapper_properties,
              )

@model_config(tablename='p2_widget', maporder=2)
class Labeltext(WidgetType):
    grok.implements(IWidgetType)   
    
    def __init__(self, objid=None):
        super(Labeltext, self).__init__(objid)
        self.register_span('label', 'label')
        self.register_span('alphanumeric', 'piggyback')

    @classmethod
    def map_computed_properties(cls):
        cls.sa_map_dispose()
        inherits = WidgetType._sa_class_manager.mapper
        orm.mapper(Labeltext,
                 inherits=inherits,
                 polymorphic_identity='labeltext',
                 properties=Labeltext.mapper_properties,
                 )
        
        
@model_config(tablename='p2_widget', maporder=2)
class Fileupload(WidgetType):
    grok.implements(IWidgetType)   
    
    js_propertyform_constructor = 'p2.FileuploadPropertyform'
    js_widget_constructor = 'p2.Widget.Fileupload'
    
    def __init__(self, objid=None):
        super(Fileupload, self).__init__(objid)
        self.register_span('label', 'label')
        self.register_span('fileupload', 'piggyback')
   
    @classmethod
    def map_computed_properties(cls):
        cls.sa_map_dispose()
        inherits = WidgetType._sa_class_manager.mapper
        orm.mapper(Fileupload,
                  inherits=inherits,
                  polymorphic_identity='fileupload',
                  properties=Fileupload.mapper_properties,
                  )


