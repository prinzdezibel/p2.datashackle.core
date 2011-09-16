# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2010
# Author:  Michael Jenny <michael.jenny%40projekt-und-partner.com>

import grok
import logging
from zope.interface import Interface
from zope.schema import List

from p2.datashackle.core.interfaces import IDatashackle
from p2.datashackle.core.interfaces import IGenericSet



class IClassDumper(Interface):
    classes = List()

class ClassDumper(grok.Adapter):
    grok.context(IGenericSet)
    grok.provides(IClassDumper)
    
    @property
    def classes(self):
        # logging.info("class name: %s \n" % self.context.__class__.__name__)
        class_list = ["%s.%s" % (cls.__module__, cls.__name__) for cls in self.context.__class__.__mro__]
        # logging.info("classes: %s \n" % class_list)
        return class_list
    
    
class ClassnameIndex(grok.Indexes):
    grok.site(IDatashackle)
    grok.context(IClassDumper)
    classes = grok.index.Text()

class PlanIdentifierIndex(grok.Indexes):
    grok.site(IDatashackle)
    grok.context(IGenericSet)
    plan_identifier = grok.index.Text()

