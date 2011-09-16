# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2011
# Author: Michael Jenny

from sqlalchemy import orm
from zope.component import getUtility

from p2.datashackle.core.app.directive import tablename, maporder
from p2.datashackle.core.interfaces import IDbUtility
from p2.datashackle.core.models.setobject_types import SetobjectType, setobject_table_registry
from p2.datashackle.core.models.linkage import Linkage
from p2.datashackle.core.models.span.span import SpanType


class Fileupload(SpanType):
    maporder(3)
    tablename('p2_span_fileupload')
    
    fileupload_label_width = 50
    fileupload_label_height = 50
    
    @classmethod
    def map_computed_properties(cls):
        cls.sa_map_dispose()
        fileupload_table = setobject_table_registry.lookup_by_class(cls.__module__, cls.__name__)
        inherits = SpanType._sa_class_manager.mapper
        orm.mapper(Fileupload,
                   fileupload_table,
                   inherits=inherits,
                   polymorphic_identity='fileupload',
                   properties=Fileupload.mapper_properties,
                  )

    def __init__(self, span_name=None, objid=None):
        self.css_style = "left:" + str(self.label_width) + "px; width:" + str(self.fileupload_label_width) + "px; height:" + str(self.fileupload_label_height) + "px; "
        self.linkage = Linkage(cardinality="n:1", ref_type="object")
        super(Fileupload, self).__init__(span_name, objid)
    
    def post_order_traverse(self, mode):
        if mode == 'save':
            self.linkage.check_if_complete()
            self.linkage.init_link()    
    
    def _get_info(self):
        info = {}
        if self.operational:
            info['media_id'] = None
            info['has_thumbnail'] = False
            info['file_name'] = None
            info['collection_id'] = self.setobject.collections[self.linkage.attr_name]['collection_id']
            info['attr_name'] = self.linkage.attr_name
            if self.media != None:
                info['has_thumbnail'] = self.media.thumbnail and True or False
                info['media_id'] = self.media.id
                info['file_name'] = self.media.filename
        return info
    
    def make_operational(self, setobject):
        super(Fileupload, self).make_operational(setobject)
        self.media = getattr(setobject, self.linkage.attr_name)

    @property
    def get_media_id(self):
        try:
            return self.media.id
        except AttributeError:
            return 0
    media_id = get_media_id
