# -*- coding: utf-8 -*-

import grok
import venusian

from pyramid.events import subscriber
from zope.app.appsetup.product import getProductConfiguration

from p2.datashackle.core.models.setobject_types import SetobjectType as Model
from p2.datashackle.core.sql import select_tables


from zope.app.wsgi.interfaces import WSGIPublisherApplicationCreated
@grok.subscribe(WSGIPublisherApplicationCreated)
def grok_init(event):
    config = getProductConfiguration('setmanager')
    init_db(config)
    init_datashackle_core()

def init_datashackle(main):
    def inner(global_config, **settings):
        init_db(settings)
        app = main(global_config, **settings)
        init_datashackle_core()
        return app
    return inner    

def init_db(settings_db):
    from p2.datashackle.core.db_utility import DbUtility
    # Instantiate the db utility to setup database connectivity.
    DbUtility(settings_db)


def init_datashackle_core():
    
    import p2.datashackle.core
    scanner = venusian.Scanner()
    scanner.scan(p2.datashackle.core, categories=('datashackle',))

    # do orm mapping
    from p2.datashackle.core.models import mapping
    mapping.orm_mapping()
    
def Session():
    from p2.datashackle.core.interfaces import IDbUtility
    from zope.component import getUtility
    util = getUtility(IDbUtility)
    return util.Session()

class model_config(object): 
    
    def __init__(self, maporder=1):
        self.maporder = maporder        

    def __call__(self, wrapped):

        def callback(context, name, factory):
            klass = factory.__name__
            proxy = select_tables(klass)
            rec = proxy.first()
            if not rec:
                raise Exception("No table for class %s." % klass)
            rec = dict(rec)
            wrapped.table_name = rec['table']
            from p2.datashackle.core.app.setobjectreg import setobject_type_registry
            setobject_type_registry.register_type(factory, self.maporder)

        info = venusian.attach(wrapped, callback, category='datashackle')

        if info.scope == 'class':
            pass
            # if the decorator was attached to a method in a class, or
            # otherwise executed at class scope, we need to set an
            # 'attr' into the settings if one isn't already in there
            #if settings['attr'] is None:
            #    settings['attr'] = wrapped.__name__
      
        return wrapped

#def _model_config(maporder=1):
#    def decorator(factory):
#        from p2.datashackle.core.app.setobjectreg import setobject_type_registry
#        setobject_type_registry.register_type(factory, maporder)
#        return factory
#    return decorator



