# -*- coding: utf-8 -*-
# Copyright(C) projekt-und-partner.com, 2011
# Author: Michael Jenny


import grok
import martian

from martian.error import GrokError

from p2.datashackle.core.app.setobjectreg import setobject_type_registry
from p2.datashackle.core.app.directive import tablename, maporder
from p2.datashackle.core.models.setobject_types import SetobjectType



class SaMappingGrokker(martian.ClassGrokker):

    martian.component(SetobjectType)
 
    def execute(self, factory, config, **kw):
        # Don't register SetobjectType base class
        if factory.__name__ == 'SetobjectType' and factory.__module__ == 'p2.datashackle.core.models.setobject_types':
            return True
        
        table_name = tablename.bind().get(factory)
        if table_name is None:
            raise GrokError('SetobjectType derived classes must specify the tablename directive '
                                '%r.' % factory, factory)
        
        # check for order directive for ordering the sequence of the mapping process
        mapordr = maporder.bind().get(factory)
        if mapordr is None:
            # Default map order
            mapordr = 1

        setobject_type_registry.register_type(factory, mapordr)
        
        return True

     




    
