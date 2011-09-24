# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2010
# Author:  Michael Jenny <michael.jenny%40projekt-und-partner.com>

import grok
import logging

from sqlalchemy import orm
from sqlalchemy.orm import exc
from grokcore.content import interfaces
from zope.component import getUtility, getMultiAdapter
from zope.location.interfaces import ILocation

from p2.datashackle.core import model_config
from p2.datashackle.core.app.setobjectreg import setobject_type_registry
from p2.datashackle.core.models.setobject_graph import SetobjectGraph
from p2.datashackle.core.models.setobject_types import SetobjectType
from p2.datashackle.core.models.widget.widget_factory import create_widget
from p2.datashackle.core.interfaces import IFormType, IDbUtility


class LocationHelper(object):
    grok.implements(ILocation)
    def __init__(self, parent):
        self.__parent__ = parent
        self.__name__ = 'forms'

@model_config(tablename='p2_form', maporder=2)
class FormType(SetobjectType):
    # In order to find default views via /index rather than
    # Zope3's /index.html we need to implement interfaces.IContext
    # The form gains location awareness (grok.url() capability) through implementing ILocation
    grok.implements(IFormType, interfaces.IContext, ILocation)

    def __init__(self, form_name=None, plan=None, objid=None, width=200, height=200):
        # BEGIN sqlalchemy instrumented attributes
        # self.form_identifier initialized through SetobjectType base class.
        self.plan = plan
        self.form_name = form_name
        self.widgets = dict()
        self.width = width
        self.height = height
        # END sqlalchemy instrumented attributes
        
        if plan != None:    
            self.plan_identifier = plan.id
            self.so_type = plan.so_type
            self.so_module = plan.so_module
        
        super(FormType, self).__init__(objid)
 
    @orm.reconstructor    
    def reconstruct(self):
        self.plan_identifier = self.plan.plan_identifier
        self.so_module = self.plan.so_module
        self.so_type = self.plan.so_type
        super(FormType, self).reconstruct()

    def common_init(self):
        super(FormType, self).common_init()
        self.__name__ =  self.form_name # Location awareness
        self.__parent__ = LocationHelper(self.plan) # Location awareness
        self.operational = False
        self.op_setobject_type = setobject_type_registry.get(self.so_module, self.so_type)
    
    def post_order_traverse(self, mode):
        super(FormType, self).post_order_traverse(mode)
        self.op_setobject_type = setobject_type_registry.get(self.so_module, self.so_type)
        if self.op_setobject_type == None:
            raise Exception("Type '%s.%s' does not exist. Check p2_plan table and/or ensure that class type exists in appropriate module and restart server." % (self.so_module, self.so_type))

    def widget_collection(self):
        for widget in self.widgets.itervalues():
            yield widget
  
    def make_operational(self, setobject):
        self.setobject = setobject
        self.op_setobject_id = setobject.id
        for (key, widget) in self.widgets.iteritems():
            widget.make_operational(setobject)
        self.operational = True
        return self
        
    def is_archetype(self):
        """ Check whether we are on an archetype form """
        return self.plan.is_archetype()
        
class WidgetTraverser(grok.Traverser):
    grok.context(FormType)

    def traverse(self, name):
        """Traversing individual widgets is done when a widget_identifier is given next."""

        db_utility = getUtility(IDbUtility)
        session = db_utility.Session()
        type = self.request.form['type']
        widget = create_widget(type)
        session.add(widget)
        session.flush()
        view = getMultiAdapter((widget, self.request), name="archetypewidget")
        # When dropping an archetype widget to the designer, it generates a widget request based on the archetype
        # form. Because this is going to be a new widget, we create an instance of the archetype.
        self.request.form['setobject_id'] = widget.id
        self.request.form['mode'] = 'DESIGNER'
        view.plan_id = self.context.plan.plan_identifier
        return view
