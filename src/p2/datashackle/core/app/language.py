# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.de, 2011
# Author: Michael Jenny

import dolmen.content
import grok

from zope.component import queryUtility, Interface
from zope.i18n import translate
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.principalannotation.interfaces import IPrincipalAnnotationUtility
from zope.publisher.browser import BrowserLanguages
from zope.publisher.interfaces.http import IHTTPRequest

from p2.datashackle.core.interfaces import IUsers, IUserPreferences


@grok.subscribe(Interface, grok.IBeforeTraverseEvent)
def before_traverse(object, event):
    request = event.request
    request.setupLocale()

    
class PreferredLanguageAdapter(BrowserLanguages, grok.Adapter):
    grok.context(IHTTPRequest)
    grok.implements(IUserPreferredLanguages)

    def getPreferredLanguages(self):
        preferred = []
        if self.request.principal != None:
            util = queryUtility(IPrincipalAnnotationUtility)
            if util:
                annot = util.getAnnotationsById(self.request.principal.id)
                if annot.get('datashackledemo'):
                    preferred.append(annot['datashackledemo']['preferred_lang'])
                    return preferred
        # default behaviour
        return super(PreferredLanguageAdapter, self).getPreferredLanguages()


