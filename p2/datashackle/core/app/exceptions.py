# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2010
# Author:  Michael Jenny <michael.jenny%40projekt-und-partner.com>


class CustomException(Exception):
    
    def _getMessage(self): 
        return self._message
    
    def _setMessage(self, message): 
        self._message = message
    
    message = property(_getMessage, _setMessage)

    def __init__(self, value=''):
        self.message = value
   
    def __str__(self):
        return self.message

class UnspecificException(CustomException):
    pass   
    
class UserException(CustomException):
    def __str__(self):
        return self.message
        
class NoPrimaryKeyException(Exception):
    def __init__(self, table_name=None, reason=None):
        self.reason = reason
        self.table_name = "(Unspecified)"
        if table_name is not None:
            self.table_name = table_name
        return
    
    def __str__(self):
        if self.reason is None:
            return "Table '" + self.table_name + "' has no usable primary key column"
        else:
            return "Table '" + self.table_name + "' has no usable primary key column: " + str(self.reason)
    
class SetobjectGraphException(Exception):
    """An exception thrown by save_setobject_graph when there was an error
    parsing the given XML graph"""
    def __init__(self, message='', setobjectid=None):
        self.reason = message
        self.setobjectid = setobjectid
        
    def __str__(self):
        returnmsg = "Setobject Graph parsing failed"
        if self.setobjectid:
            returnmsg += " (at id " + self.setobjectid + ")"
        if self.reason:
            if len(self.reason) > 0:
                returnmsg += ": " + self.reason
        return returnmsg

class InvalidWidgetDataType(CustomException):
    pass

class InvalidContext(CustomException):
    pass

class DataSchemaError(CustomException):
    pass

class InvalidCompositeMode(CustomException):
    """An exception type that is thrown if a setmanager composite (plan, form,
    widget, span) is either in instance mode nor in type mode, that means its mode
    is undefined."""

class MissingRequestParameter(CustomException):
    """Indicates a missing http request parameter."""
    
