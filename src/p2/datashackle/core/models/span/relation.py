# -*- coding:utf-8 -*-
# Copyright(C) projekt-und-partner.com, 2011
# Author: Michael Jenny

from sqlalchemy import orm
from zope.component import getUtility

from p2.datashackle.core import model_config
from p2.datashackle.core.app.setobjectreg import setobject_table_registry, setobject_type_registry
from p2.datashackle.core.interfaces import IDbUtility
from p2.datashackle.core.models.setobject_types import SetobjectType
from p2.datashackle.core.models.span.span import SpanType
from p2.datashackle.core.models.linkage import Linkage
from zope.component import getUtility
from p2.datashackle.core.app.setobjectreg import setobject_table_registry, setobject_type_registry


@model_config(tablename='p2_span_relation', maporder=3)
class Relation(SpanType):
    
    height = 50
    width = 50
 
    def __init__(self, span_name=None, objid=None):
        self.linkage = Linkage()
        self.css_style = "left:" + str(self.label_width) + "px; width:" + \
            str(self.width) + "px; height:" + str(self.height) + "px;"
        super(Relation, self).__init__(span_name, objid)
    
    def __setattr__(self, name, value):
        SpanType.__setattr__(self, name, value)
        if name == 'linkage':
            if self.plan_identifier != None and value != None:
                # Get the table identifier from our plan identifier and set it as the linkage's target class
                table = setobject_table_registry.lookup_by_table('p2_plan')
                plan = getUtility(IDbUtility).engine.execute(table.select(table.c.plan_identifier == self.plan_identifier)).first()
                assert(plan != None)
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

    def post_order_traverse(self, mode):
        if mode == 'save':
            self.linkage.check_if_complete()
            self.linkage.init_link()
 
    def _get_info(self):
        info = {}
        if self.operational:
            info['linkage_id'] = self.linkage.id
        return info

    @classmethod
    def map_computed_properties(cls):
        cls.sa_map_dispose()
        relation_table = setobject_table_registry.lookup_by_class(cls.__module__, cls.__name__)
        inherits = SpanType._sa_class_manager.mapper
        orm.mapper(Relation,
                   relation_table, # We want joined table inheritance for the relation span (additional table for relation specific fields)
                   inherits=inherits,
                   polymorphic_identity='relation',
                   properties=cls.mapper_properties
                   )
        

