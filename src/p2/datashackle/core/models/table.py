# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2011
# Author: Michael Jenny

import sqlalchemy

from p2.datashackle.core.app.exceptions import UnspecificException


class Table(sqlalchemy.Table):
    
    def get_primary_key_column(self):
        """Returns the name of the primarykey column."""
        primarykeyobj = self.primary_key
        columns_dictset = primarykeyobj.columns
        columns_keys = primarykeyobj.columns.keys()
        if len(columns_keys) != 1:
            raise UnspecificException("Either there is no primary key or it is a composite one. Can't work with that.")
        column = columns_dictset[columns_keys[0]]
        return column

    def get_column(self, name):
        """Returns a column by name"""
        return getattr(self.c, name)


