# -*- coding:utf-8 -*-
# Copyright(C) projekt-und-partner.com, 2011
# Author: Michael Jenny

from sqlalchemy import orm
from zope.component import getUtility

from p2.datashackle.core import model_config
from p2.datashackle.core.app.exceptions import SetobjectGraphException
from p2.datashackle.core.app.setobjectreg import setobject_table_registry, setobject_type_registry
from p2.datashackle.core.interfaces import IDbUtility
from p2.datashackle.core.models.span.span import SpanType
from p2.datashackle.core.models.linkage import Linkage
from zope.component import getUtility


@model_config(tablename='p2_span_dropdown', maporder=2)
class Dropdown(SpanType):
   
    width = 95
 
    def __init__(self, span_name=None, objid=None):
        self.linkage = Linkage(
            cardinality='n:1',
            ref_type='object',
            target_module='',
        )
        self.css_style = "left:" + str(self.label_width) + "px; width:" + str(self.width) + "px;"
        super(Dropdown, self).__init__(span_name, objid)
    
    def onbefore_post_order_traverse(self, setobject, mode):
        if self.required == True and getattr(setobject, self.linkage.attr_name) is None and mode == 'save':
            raise SetobjectGraphException("Please select a value for '" + self.widget.spans['label'].span_value + "'.")

    def post_order_traverse(self, mode):
        if mode == 'save':
            self.linkage.source_module = self.op_setobject_type.__module__
            self.linkage.source_classname =  self.op_setobject_type.__name__
            self.linkage.check_if_complete()
            self.linkage.init_link()
     
    def __setattr__(self, name, value):
        SpanType.__setattr__(self, name, value)
        if name == 'linkage':
            if self.plan_identifier != None and value != None:
                # Get the table identifier from our plan identifier and set it as the linkage's target class
                table = setobject_table_registry.lookup_by_table('p2_plan')
                plan = getUtility(IDbUtility).engine.execute(table.select(table.c.plan_identifier == self.plan_identifier)).first()
                plan_module = plan['so_module']
                plan_type = plan['so_type']
                table_identifier = setobject_type_registry.lookup(plan_module, plan_type).get_table_name()
                oldtargetclass = None
                try:
                    oldtargetclass = self.linkage.target_classname
                except AttributeError:
                    pass
                if oldtargetclass == None or oldtargetclass == "":
                    self.linkage.target_classname = table_identifier
        
    def _get_info(self):
        info = {}
        if self.operational:
            info['linkage_id'] = self.linkage.id
            info['attr_name'] = self.attr_name
        return info

    @classmethod
    def map_computed_properties(cls):
        cls.sa_map_dispose()
        table = setobject_table_registry.lookup_by_class(cls.__module__, cls.__name__)
        inherits = SpanType._sa_class_manager.mapper
        orm.mapper(Dropdown,
                   table,
                   inherits=inherits,
                   polymorphic_identity='dropdown',
                   properties=cls.mapper_properties
                   )
        

