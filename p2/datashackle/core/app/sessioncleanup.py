# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2010
# Author:  Jonas Thiem <jonas.thiem%40projekt-und-partner.com>


from p2.datashackle.core.interfaces import IDbUtility

from zope.publisher.interfaces import IEndRequestEvent
from zope.component import getUtility
import grok
from sqlalchemy.orm import sessionmaker, scoped_session

@grok.subscribe(IEndRequestEvent)
def CleanupSession(event):
    dbutil = getUtility(IDbUtility)
    if hasattr(dbutil, 'Session'):
        dbutil.Session.rollback()
        dbutil.Session.remove()
