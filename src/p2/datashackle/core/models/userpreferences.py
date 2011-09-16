# -*- coding:utf-8 -*-
# Copyright (C) projekt-und-partner.de, 2011
# Author: Michael Jenny

import grok

from zope.component import getUtility
from zope.schema.fieldproperty import FieldProperty
from zope.security.interfaces import IPrincipal
from zope.securitypolicy.interfaces import IPrincipalRoleManager, IPrincipalPermissionManager
from zope.principalannotation.interfaces import IPrincipalAnnotationUtility

from p2.container.container import ignore_enumeration
from p2.datashackle.core import globals
from p2.datashackle.core.interfaces import IUserPreferences


class MappingProperty(object):
    
    def __init__(self, name):
        self.name = name
   
    def __get__(self, inst, class_=None):
        util = getUtility(IPrincipalAnnotationUtility)
        info = util.getAnnotationsById(inst.context.id)
        if not info.get('datashackledemo'):
            return None
        return info['datashackledemo'][self.name]

    def __set__(self, inst, value):
        util = getUtility(IPrincipalAnnotationUtility)
        info = util.getAnnotationsById(inst.context.id)
        if not info.get('datashackledemo'):
            info['datashackledemo'] = dict()
        info['datashackledemo'][self.name] = value


class UserPreferences(grok.Model, grok.Adapter):
    grok.implements(IUserPreferences)
    grok.context(IPrincipal)
    grok.provides(IUserPreferences)

    title = FieldProperty(IUserPreferences['title'])
 
    preferred_lang = MappingProperty('preferred_lang')
    preferred_date = MappingProperty('preferred_date')


@grok.subscribe(UserPreferences, grok.IObjectAddedEvent)
def user_preferences_added(obj, event):
    # grant local permission
    principal = obj.context
    principal_roles = IPrincipalRoleManager(obj)
    principal_roles.assignRoleToPrincipal('setmanager.Owner', principal.id)

    if principal.id != "zope.manager" and globals.manager_preferences:
        # Don't allow the edit and index view of the parent container for non-manager principals
        parent = obj.__parent__
        principal_permission = IPrincipalPermissionManager(parent)
        principal_permission.denyPermissionToPrincipal('dolmen.content.View', principal.id)
        principal_permission.denyPermissionToPrincipal('dolmen.content.Edit', principal.id)
        # Ignore zope.Manager UserPreferences when container is enumerated
        ignore_enumeration(globals.manager_preferences, principal.id)

