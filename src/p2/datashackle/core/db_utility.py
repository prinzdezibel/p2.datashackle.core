# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2010
# Author:  Michael Jenny <michael.jenny%40projekt-und-partner.com>

import grok
import sys
import logging
import zope.component

from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import OperationalError
from zope.component import getUtility, queryUtility
from zope.catalog.interfaces import ICatalog
from zope.app.appsetup.interfaces import IDatabaseOpenedWithRootEvent
from zope.component import getGlobalSiteManager
from zope.component import getUtility
from zope.event import notify
from zope.interface import Interface

from p2.datashackle.core.sql import max_allowed_packet_sql
from p2.datashackle.core.interfaces import *
from p2.datashackle.core.globals import metadata



class RelationalDatabaseOpened(object):
    grok.implements(IRelationalDatabaseOpened)


class DbUtility(object):
    grok.provides(IDbUtility)
    
    def __init__(self, settings):
        # register instance as global utility.
        gsm = getGlobalSiteManager()
        gsm.registerUtility(self, IDbUtility)

        self.settings = settings
        
        connection_string = self.getConnectionString()
        
        self.engine = create_engine(
            connection_string,
            echo=False,
            encoding='utf-8',
            convert_unicode=True,
        )
        # Make a test query and at the same time, obtain max_allowed_packet
        self.max_allowed_packet = self.engine.scalar(max_allowed_packet_sql())
    
        # bind engine to the metadata
        metadata.bind = self.engine
   
        # We'll have to stick with scoped sesssions because of threading
        # See: http://www.mail-archive.com/zope-dev@zope.org/msg25090.html
        self.Session = scoped_session(sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
        ))

        grok.notify(RelationalDatabaseOpened())        
            
    def getConnectionString(self):
        """Builds the connection string.
        Read also: http://www.sqlalchemy.org/docs/dialects/mysql.html#character-sets
        """
        if self.settings['datashackle.db_provider'] == 'mysql':
            provider = 'mysql+mysqldb'
        else:
            provider = self.settings['datashackle.db_provider']
        return "%s://%s:%s@%s/%s?charset=utf8&use_unicode=0" % (
            provider,
            self.settings['datashackle.db_user'],
            self.settings['datashackle.db_password'],
            self.settings['datashackle.db_host'],
            self.settings['datashackle.db_name'])
        
        
