# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2011
# Author:  Michael Jenny <michael.jenny%40projekt-und-partner.com>

from sqlalchemy import orm

from p2.datashackle.core import ModelBase, model_config


@model_config()
class Cardinality(ModelBase):

    @classmethod
    def sa_map(cls):
        #cls.sa_map_dispose()
        #cardinality_type.sa_map_dispose()
        orm.mapper(cls, cls.get_table_class())

    def __init__(self):
        self.id = 'NONE'

    def __str__(self):
        return self.id
