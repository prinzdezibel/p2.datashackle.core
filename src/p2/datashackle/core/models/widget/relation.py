# -*- coding: utf-8 -*-
# Copyright(C) projekt-und-partner.com, 2011
# Author: Jonas Thiem

import grok

from sqlalchemy import orm
from zope.component import getUtility

from p2.datashackle.core import model_config
from p2.datashackle.core.app.setobjectreg import setobject_type_registry
from p2.datashackle.core.interfaces import IWidgetType, IDbUtility
from p2.datashackle.core.models.widget.widget import WidgetType

@model_config(tablename='p2_widget', maporder=2)
class Relation(WidgetType):
    grok.implements(IWidgetType)

    js_propertyform_constructor = 'p2.RelationPropertyform'
    
    def __init__(self, objid=None):
        super(Relation, self).__init__(objid)
        self.register_span('label', 'label')
        self.register_span('relation', 'piggyback')

    @classmethod
    def map_computed_properties(cls):
        cls.sa_map_dispose()
        inherits = WidgetType._sa_class_manager.mapper
        orm.mapper(Relation,
            inherits=inherits,
            properties=Relation.mapper_properties,
            polymorphic_identity='relation')

