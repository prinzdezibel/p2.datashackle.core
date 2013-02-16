# -*- coding: utf-8 -*-

from p2.datashackle.core import model_config
from p2.datashackle.core.models.setobject_types import SetobjectType
from sqlalchemy import orm


@model_config()
class Model(SetobjectType):
    @classmethod
    def sa_map(cls):
        orm.mapper(cls, cls.get_table_class())

