# -*- coding utf-8 -*-
# Copyright (C) projekt-und-partner.de, 2011
# Author: Michael Jenny

import grok

from zope.i18n import translate
from zope.publisher.interfaces import IRequest
from zope.schema.fieldproperty import FieldProperty
from zope.security.interfaces import NoInteraction
from zope.security.management import getInteraction

from p2.datashackle.core.interfaces import ITranslatableDescriptiveProperties



class TranslatableDescriptiveProperties(object):
    grok.implements(ITranslatableDescriptiveProperties)
    
    def get_title(self):
        try:
            request = getRequest()
            return translate(self._title, context=request)
        except NoInteraction:
            return self._title
    
    def set_title(self, value):
        self._title = value

    title = property(get_title, set_title)
    


def getRequest():
    i = getInteraction() # raises NoInteraction

    for p in i.participations:
        if IRequest.providedBy(p):
            return p

    raise RuntimeError('Could not find current request.')

        

