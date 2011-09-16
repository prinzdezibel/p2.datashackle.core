# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2010
# Author:  Michael Jenny <michael.jenny%40projekt-und-partner.com>

import grok
import sys
import logging
import zope.component

from subprocess import Popen,PIPE
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import OperationalError
from zope.component import getUtility, queryUtility
from zope.catalog.interfaces import ICatalog
from zope.app.appsetup.interfaces import IDatabaseOpenedWithRootEvent
from zope.component import getUtility
from zope.app.appsetup.product import getProductConfiguration
from zope.event import notify
from zope.interface import Interface

from p2.datashackle.core.sql import max_allowed_packet_sql
from p2.datashackle.core.interfaces import *
from p2.datashackle.core.globals import metadata



class RelationalDatabaseOpened(object):
    grok.implements(IRelationalDatabaseOpened)


class ConnectionSettings(object):
   
    def __init__(self, connection_params=None):
        if not connection_params:
            self.auto_detect_connection_params()
        else:
            self.set_connection_params(connection_params)

    def auto_detect_connection_params(self):
        """Connection parameters may come from a config file or from another user storage (local utility)."""
        IDatabaseSettings = queryUtility(Interface, name='IDatabaseSettings')
        if IDatabaseSettings:
            utility = queryUtility(IDatabaseSettings)
            if utility:
                self.settings = {'db_provider': utility.DBProvider,
                                 'db_host': utility.HostAddress,
                                 'db_user': utility.LoginName,
                                 'db_password': utility.getTrueLoginPassword(),
                                 'db_name': utility.DBName
                                 }
        self.set_settings_from_config()
 
    def set_connection_params(self, params):
        if type(params) != dict:
            raise TypeError("params must be passed as dict")
        if 'db_provider' not in params:
            raise KeyError("db_provider param is obligatory.")
        if 'db_user' not in params:
            raise KeyError("db_user param is obligatory.")
        if 'db_password' not in params:
            raise KeyError("db_password param is obligatory.")
        if 'db_host' not in params:
            raise KeyError("db_host param is obligatory.")
        if 'db_name' not in params:
            raise KeyError("db_name param is obligatory.")
        self.settings = params
    
    def set_settings_from_config(self):
        """ Initialize settings from config file."""
        config = getProductConfiguration('setmanager')
        self.settings = {'db_provider': config.get('db_provider'),
                         'db_host': config.get('db_host'),
                         'db_user': config.get('db_user'),
                         'db_password': config.get('db_password'),
                         'db_name': config.get('db_name')
                         }
    
    def get_settings(self):
        return self.settings

    def get_connection_string(self):
        """Builds the connection string.
        Read also: http://www.sqlalchemy.org/docs/dialects/mysql.html#character-sets
        """
        if not hasattr(self, 'settings') or self.settings == None:
            raise UnspecificException("Connection params must be setted either explicitely through " +
                "set_connection_params or via auto_detect_connection_params.")
        if self.settings['db_provider'] == 'mysql':
            provider = 'mysql+mysqldb'
        else:
            provider = self.settings['db_provider']
        return "%s://%s:%s@%s/%s?charset=utf8&use_unicode=0" % (provider,
            self.settings['db_user'], self.settings['db_password'], self.settings['db_host'], self.settings['db_name'])
    

class DbUtility(grok.GlobalUtility):
    grok.provides(IDbUtility)
    
    def __init__(self):
        self.engine = None
        self.vars = None
        self.db_lock_scheduled = False
        self.db_locked = False # we have no db -> we can safely change settings
        self.executeconnection = None # our stored SQLAlchemy connection to execute stuff
       
 
    def setup_database(self):
        if not self.vars:
            # No database settings given. Don't try at all
            self.engine = None
            return False
            
        if (self.engine is not None):
            self.engine.pool.dispose()
            del(self.engine)
            self.Session = None
        
        connection_string = self.getConnectionString()
        try:
            self.engine = create_engine(
                connection_string,
                echo=False,
                encoding='utf-8',
                convert_unicode=True,
            )
            # Make a test query and at the same time, obtain max_allowed_packet
            sql = max_allowed_packet_sql(self.db_provider)
            self.max_allowed_packet = self.engine.scalar(sql)
        except:
            self.engine = None
            raise
    
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
            
        return True
    
    def checkDatabaseDuringLock(self):
        """ DB is locked and we want to test whether we can successfully use another one (new settings).
        """
        return self.doDatabaseLogin(True) # is the database usable?
                    
    
    def executesql(self, line):
        """ Execute an SQL command in text form - works only if the database is locked and a connection is
            available.
        """
        if not self.engine:
            return
        if not self.db_locked:
            return
        if not self.executeconnection:
            self.executeconnection = self.engine.connect()
        self.executeconnection.execute(text(line))

    def unlock(self):
        """ Unlock database again """
        if self.executeconnection:
            self.executeconnection.close()
            self.executeconnection = None
        # remove lock variables on generic sets
        catalog = getUtility(ICatalog)
        sets = catalog.searchResults(classes = 'menhir.contenttype.nosqlmyadmin.generic_set.GenericSet')
        for genericset in sets:
            try:
                genericset.db_lock_scheduled = 0
            except (AttributeError,NameError):
                pass
        # force all generic sets to reload their plans
        self.db_locked = False
        self.db_lock_scheduled = False
        self.updateDatabase(False, True)

    def didSettingsChange(self, oldsettings, newsettings):
        """ Check whether the settings have been altered """
        if (not oldsettings):
            if (not newsettings):
                return False
            return True
        if (oldsettings['db_name'] != newsettings['db_name'] or
            oldsettings['db_host'] != newsettings['db_host'] or
            oldsettings['db_password'] != newsettings['db_password'] or
            oldsettings['db_user'] != newsettings['db_user'] or
            oldsettings['db_provider'] != newsettings['db_provider']):
            return True
        return False
        

    def getSettingsDataFromConfig(self):
        """ Initialize settings from config """
        config = getProductConfiguration('setmanager')
        try:
            return {
                'db_provider': config.get('db_provider'),
                'db_host': config.get('db_host'),
                'db_user': config.get('db_user'),
                'db_password': config.get('db_password'),
                'db_name': config.get('db_name')
            }
        except:
            pass
    
    def getConnectionString(self):
        """Builds the connection string.
        Read also: http://www.sqlalchemy.org/docs/dialects/mysql.html#character-sets
        """
        settings = self.getSettingsData()
        if settings['db_provider'] == 'mysql':
            provider = 'mysql+mysqldb'
        else:
            provider = settings['db_provider']
        return "%s://%s:%s@%s/%s?charset=utf8&use_unicode=0" % (provider, settings['db_user'], settings['db_password'], settings['db_host'], settings['db_name'])
        
    def getSettingsData(self):
        """ Initialize settings from DatabaseSettings if available. otherwise obtains config values """
        IDatabaseSettings = queryUtility(Interface, name='IDatabaseSettings')
        if IDatabaseSettings:
            utility = queryUtility(IDatabaseSettings)
            if utility:
                return {
                    'db_provider': utility.DBProvider,
                    'db_host': utility.HostAddress,
                    'db_user': utility.LoginName,
                    'db_password': utility.getTrueLoginPassword(),
                    'db_name': utility.DBName
                    }
        return self.getSettingsDataFromConfig()
           
    
    
    def updateDatabase(self, OnlyIfDisconnected=True, ForceNewInitialization=False):
        """ Update the database config.
            If OnlyIfDisconnected is true then only change settings if there is no SQL available yet (otherwise
            just do nothing).
            If ForceNewInitialization is true, then all plans of all generic sets are going to be reloaded and
            freshly initialized even if nothing has changed.
        """
        if (OnlyIfDisconnected == False or not self.engine or ForceNewInitialization):
            newvars = self.getSettingsData()
            if (self.didSettingsChange(self.vars, newvars) or self.engine is None):
                oldvars = self.vars
                self.vars = newvars
                logging.debug("Database configuration changed: " + str(self.vars))
                try:
                    if self.setup_database() == False:
                        self.vars = oldvars
                except OperationalError:
                    self.vars = oldvars
                return
            else:
                #if ForceNewInitialization:
                #   self.checkAllReferences() # reload all plans anyway
                pass
        return
    
    def dropdbcontents(self):
        if not self.engine or not self.db_locked:
            return
        meta = MetaData(self.engine)
        meta.reflect()
        meta.drop_all()
        
    def isDatabaseAvailable(self, ignoreLock=False):
        """ Update internal variables, check if database is available
            Can return either True (is available) or False (not available - don't use SQLAlchemy session!!)
        """
        if self.db_locked and not ignoreLock:
            return False
        if self.engine:
            return True
        self.updateDatabase(True, ignoreLock)
        if not self.engine:
            return False
        return True
        
    # properties
    @property
    def db_host(self):
        if (self.vars == None):
            return None
        return self.vars['db_name']
    
    @property
    def db_provider(self):
        if (self.vars == None):
            return None
        return self.vars['db_provider']
    
    @property
    def db_name(self):
        if (self.vars == None):
            return None
        return self.vars['db_name']

#@grok.subscribe(IDatabaseOpenedWithRootEvent)
#def GetAvailableSchemaVersions(event):
#    config = getProductConfiguration('setmanager')
#    buildout_root = config['buildout_root']
#    db_utility = getUtility(IDbUtility)
#    db_utility.schemaversion = int(Popen([buildout_root + "/bin/sqlversioning.py","version"], stdout=PIPE).communicate()[0])
