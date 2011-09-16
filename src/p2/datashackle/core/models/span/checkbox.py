# -*- coding: utf-8 -*-
# Copyright(C) projekt-und-partner.com, 2011
# Author: Michael Jenny

from sqlalchemy import orm
from sqlalchemy import Boolean

from p2.datashackle.core.app.directive import tablename, maporder
from p2.datashackle.core.models.mapping import map_field_attr
from p2.datashackle.core.models.setobject_types import setobject_table_registry, \
    setobject_type_registry
from p2.datashackle.core.models.span.span import SpanType


class Checkbox(SpanType):
    maporder(3)
    tablename('p2_span_checkbox')

    @classmethod
    def map_computed_properties(cls):
        cls.sa_map_dispose()
        table = setobject_table_registry.lookup_by_class(cls.__module__, cls.__name__)
        inherits = SpanType._sa_class_manager.mapper
        orm.mapper(Checkbox,
                    table, # Joined table inheritance
                    inherits=inherits,
                    polymorphic_identity='checkbox',
                    properties=cls.mapper_properties,
                  )

    def __init__(self, span_name=None, objid=None):
        self.css_style = "left:" + str(self.label_width) + "px;"
        super(Checkbox, self).__init__(span_name, objid)

    def _get_info(self):
        info = {}
        if self.operational:
            info['piggyback'] = self.piggyback
            info['attr_name'] = self.attr_name
        return info
    
    def post_order_traverse(self, mode):
        if mode == 'save':
            so_type = setobject_type_registry.lookup(
                self.op_setobject_type.__module__,
                self.op_setobject_type.__name__)
            table_name = so_type.get_table_name()
            map_field_attr(
                table_name,
                self.field_identifier,
                Boolean)
 
    def make_operational(self, setobject):
        super(Checkbox, self).make_operational(setobject)
        if getattr(setobject, self.attr_name) == None:
            self.piggyback = self.span_value
        else:
            self.piggyback = getattr(setobject, self.attr_name)


        
