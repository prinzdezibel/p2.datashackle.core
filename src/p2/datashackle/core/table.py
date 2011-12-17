# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2011
# Author: Michael Jenny

import sqlalchemy

from p2.datashackle.core.app.exceptions import UnspecificException


#class Table(sqlalchemy.Table):
#    
#    def get_primary_key_column(self):
#        """Returns the name of the primarykey column."""
#        columns = self.primary_key.columns
#        columns_keys = columns.keys()
#        if len(columns_keys) != 1:
#            raise UnspecificException("Either there is no primary key or it is a composite one. Can't work with that.")
#        column = columns[columns_keys[0]]
#        return column
#
#    def get_primary_key_attr_name(self):
#        column = self.get_primary_key_column()
#        return column.name

