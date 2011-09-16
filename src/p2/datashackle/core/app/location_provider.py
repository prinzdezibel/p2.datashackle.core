# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2010
# Author:  Michael Jenny <michael.jenny%40projekt-und-partner.com>

import grok

from zope.catalog.interfaces import ICatalog
from zope.component import getUtility

from p2.datashackle.core.interfaces import ILocationProvider


class LocationProvider(grok.GlobalUtility):
    grok.provides(ILocationProvider)
    
    def locate_attrs(self, plan_identifier):
        catalog = getUtility(ICatalog)
        genericsets = catalog.searchResults(classes='p2.datashackle.management.generic_set.GenericSet')
        for genericset in genericsets:
            if genericset.plan_identifier == plan_identifier:
                return genericset.__name__, genericset.__parent__
        raise Exception("Can't provide location information of Plan '%s'" % plan_identifier)

    def lookup_genericset(self, plan_identifier):
        genericset = self.get_genericset(plan_identifier)
        if genericset == None:
            raise Exception("Genericset %s not found via catalog." % plan_identifier)     
        return genericset     

    def get_genericset(self, plan_identifier):
        catalog = getUtility(ICatalog)
        resultset = catalog.searchResults(classes='p2.datashackle.management.generic_set.GenericSet',
                                          plan_identifier=plan_identifier)
        if len(resultset) == 0:
            return None
        else:
            return iter(resultset).next()
    
    def lookup_plan(self, plan_identifier):
        generic_set = self.get_genericset(plan_identifier)
        if generic_set is None:
            raise Exception("No genericset for plan '%s' found." % plan_identifier)
        return generic_set._plan_internal
            
