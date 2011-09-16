# -*- coding: utf-8 -*-
# Copyright(C) 2011, projekt-und-partner.com
# Author: Michael Jenny


class SetobjectTableRegistry(object):

    def __init__(self):
        self._table_name = dict()
        self._class_name = dict()

    def register_type(self, module_name, class_name, table_name, table_type):
        """Creates a SQLAlchemy table object from a given file and registers it in the registry.
        """
        
        # store it in registry under two different keys
        self._table_name[table_name] = table_type
        key = self._assemble_key(module_name, class_name)
        self._class_name[key] = table_type

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
    
    def lookup_by_class(self, module_name, class_name):
        key = self._assemble_key(module_name, class_name)
        return self._class_name[key]

    def _assemble_key(self, module_name, class_name):
        return module_name + '.' + class_name

setobject_table_registry = SetobjectTableRegistry()


class SetobjectTypeRegistry(object):

    def __init__(self):
        self._setobject_types = dict()

    def register_type(self, setobject_type, maporder):
        key = self._assemble_key(setobject_type.__module__, setobject_type.__name__)
        self._setobject_types[key] = (maporder, setobject_type)
    
    def delete_by_table(self, table_name):
        for (key,sotype) in self._setobject_types.items():
            if sotype[1].get_table_name() == table_name:
                del(self._setobject_types[key])
    
    def lookup_by_table(self, table_name):
        for (key,sotype) in self._setobject_types.items():
            if sotype[1].get_table_name() == table_name:
                return self._setobject_types[key][1]
        return None

    def get(self, module, name):
        if module == None or name == None:
            return None
        key = self._assemble_key(module, name)
        t = self._setobject_types.get(key)
        if t == None:
            return None
        else:
            return t[1]

    def lookup(self, module, name):
        key = self._assemble_key(module, name)
        return self._setobject_types[key][1]
    
    def _assemble_key(self, module, name):
        return module + '.' + name
       
    def values(self):
        """A generator that yields all registered setobject types."""
        type_list = [t for t in self._setobject_types.itervalues()]
        sortd = sorted(type_list, key=lambda entry: entry[0])
        for (_, setobject_type) in sortd:
            yield setobject_type

setobject_type_registry = SetobjectTypeRegistry()

