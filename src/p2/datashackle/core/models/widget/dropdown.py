# -*- coding: utf-8 -*-
# Copyright(C) projekt-und-partner.com, 2011
# Author: Michael Jenny

import grok

from sqlalchemy import orm

from p2.datashackle.core import model_config
from p2.datashackle.core.interfaces import IWidgetType
from p2.datashackle.core.models.widget.widget import WidgetType


@model_config(tablename='p2_widget', maporder=2) 
class Dropdown(WidgetType):
    grok.implements(IWidgetType)
    
    js_propertyform_constructor = 'p2.DropdownPropertyform'
    
    def __init__(self, objid=None):
        super(Dropdown, self).__init__(objid)
        self.register_span('label', 'label')
        self.register_span('dropdown', 'piggyback')

    @classmethod
    def map_computed_properties(cls):
        cls.sa_map_dispose()
        inherits = WidgetType._sa_class_manager.mapper
        orm.mapper(Dropdown,
            inherits=inherits,
            properties=Dropdown.mapper_properties,
            polymorphic_identity='dropdown')

