# -*- coding: utf-8 -*-
# Copyright(C) 2011, projekt-und-partner.com
# Author: Michael Jenny


class SetobjectTableRegistry(object):

    def __init__(self):
        self._table_name = dict()
        self._class_name = dict()

    def register_type(self, class_name, table_name, table_type):
        """Creates a SQLAlchemy table object from a given file and registers it in the registry.
        """
        # store it in registry under two different keys
        self._table_name[table_name] = table_type
        self._class_name[class_name] = table_type

    def get_by_table(self, table_name):
        if table_name in self._table_name:
            return self._table_name[table_name]
        else:
            return None
    
    def lookup_by_table(self, table_name):
        """Looks up a table type in the registry. Raises exception if not found."""
        return self._table_name[table_name]
    
    def delete_by_table(self, table_name):
        if table_name in self._table_name:
            del(self._table_name[table_name])
            for key,table in self._class_name.items():
                if table.name == table_name:
                    del(self._class_name[key])
    
    def lookup_by_class(self, class_name):
        return self._class_name[class_name]


setobject_table_registry = SetobjectTableRegistry()


class SetobjectTypeRegistry(object):

    def __init__(self):
        self._models = dict()

    def register_type(self, setobject_type, maporder):
        print "class: %s:%s" % (setobject_type.__name__, setobject_type.__module__)
        if setobject_type.__name__ in self._models:
            raise Exception("Class name %s already exists. Choose a unique class name." % setobject_type.__name__)
        self._models[setobject_type.__name__] = (maporder, setobject_type)
    
    def delete_by_table(self, table_name):
        for (key,sotype) in self._models.items():
            if sotype[1].get_table_name() == table_name:
                del(self._models[key])
    
    def lookup_by_table(self, table_name):
        for (key,sotype) in self._models.items():
            if sotype[1].get_table_name() == table_name:
                return self._models[key][1]
        return None

    def get(self, name):
        if name == None:
            return None
        t = self._models.get(name)
        if t == None:
            return None
        else:
            return t[1]

    def lookup(self, name):
        return self._models[name][1]
    
    def values(self):
        """A generator that yields all registered setobject types."""
        type_list = [t for t in self._models.itervalues()]
        sortd = sorted(type_list, key=lambda entry: entry[0])
        for (_, setobject_type) in sortd:
            yield setobject_type

setobject_type_registry = SetobjectTypeRegistry()

