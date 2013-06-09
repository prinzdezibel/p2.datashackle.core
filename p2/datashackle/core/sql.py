# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2010
# Author:  Michael Jenny <michael.jenny%40projekt-und-partner.com>

from sqlalchemy import *
from zope.component import getUtility

from p2.datashackle.core.app.exceptions import *
from p2.datashackle.core.interfaces import IDbUtility


def max_allowed_packet_sql():
    db_utility = getUtility(IDbUtility)
    if db_utility.settings['datashackle.db_provider'] == 'mysql':
         return "SELECT @@max_allowed_packet"
    else:
        raise UnspecificException("Unknown database provider")
    
def table_exists(table_name):
    db_utility = getUtility(IDbUtility)
    if db_utility.settings['datashackle.db_provider'] == 'mysql':
        stmt = "SELECT TABLE_NAME FROM information_schema.TABLES " \
            "WHERE TABLE_SCHEMA = '" + db_utility.settings['datashackle.db_name'] + "' AND " \
            "TABLE_TYPE = 'BASE TABLE' AND TABLE_NAME = '" + table_name + "'"
    else:
        raise UnspecificException("Unknown database provider.")
    return db_utility.engine.execute(stmt).first() is not None

def select_tables(klass=None):
    db_utility = getUtility(IDbUtility)
    if db_utility.settings['datashackle.db_provider'] == 'mysql':
        stmt = "SELECT klass, `table` FROM p2_model"
        if klass:
            stmt += " WHERE klass = '%s'" % klass
    else:
        raise UnspecificException("Unknown database provider.")
    return db_utility.engine.execute(stmt)

#def get_tables():
#    db_utility = getUtility(IDbUtility)
#    if db_utility.settings['datashackle.db_provider'] == 'mysql':
#        stmt = "SELECT TABLE_NAME FROM information_schema.TABLES " \
#            "WHERE TABLE_SCHEMA = '" + db_utility.settings['datashackle.db_name'] + "' AND " \
#            "TABLE_TYPE = 'BASE TABLE'"
#    else:
#        raise UnspecificException("Unknown database provider.")
#    return db_utility.engine.execute(stmt)

def field_exists(table_identifier, field_identifier):
    db_utility = getUtility(IDbUtility)
    if db_utility.settings['datashackle.db_provider'] == 'mysql':
        stmt = "SELECT COUNT(*) FROM information_schema.COLUMNS " \
            "WHERE TABLE_SCHEMA = '" + db_utility.settings['datashackle.db_name'] + "' AND TABLE_NAME = " \
            "'" + str(table_identifier) + "' AND COLUMN_NAME = " \
            "'" + str(field_identifier) + "'"
    else:
        raise UnspecificException("Unknown database provider.")

    if db_utility.engine.scalar(stmt) == 0:
        return False
    else:
        return True
