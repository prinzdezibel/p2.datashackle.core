# -*- coding: utf-8 -*-
from p2.datashackle.core import model_config
from p2.datashackle.core.models.setobject_types import SetobjectType
from sqlalchemy import orm

from p2.datashackle.core.app.setobjectreg import setobject_table_registry, setobject_type_registry



@model_config()
class StrippedModel(SetobjectType):
    """Operates like Plan on p2_plan without the need to import the Plan class type.
        It has the same instrumented attributes like Plan.
    """
    @classmethod
    def sa_map(cls):
        orm.mapper(cls, cls.get_table_class())

