# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2011
# Author:  Michael Jenny <michael.jenny%40projekt-und-partner.com>

from sqlalchemy import Column, Table
from sqlalchemy import orm
from sqlalchemy.schema import ForeignKey

from p2.datashackle.core import model_config, Session
from p2.datashackle.core.app.setobjectreg import setobject_table_registry, \
    setobject_type_registry
from p2.datashackle.core.app.exceptions import UserException
from p2.datashackle.core.models import Model
from p2.datashackle.core.models.cardinality import Cardinality
from p2.datashackle.core.sql import field_exists


@model_config()
class Relation(Model):
    """The relation class represents and manages database relations.
    """    

    def __init__(self, cardinality='ONE_TO_MANY'):
        session = Session()
        self.cardinality = session.query(Cardinality). \
            filter(Cardinality.id == str(cardinality)).one()
            
        super(Relation, self).__init__()
        
    def post_order_traverse(self, mode):
        if mode == 'save':
            pass

    @classmethod
    def sa_map(cls):
        cardinality_type = setobject_type_registry.lookup(
            'Cardinality'
        )
        orm.mapper(cls,
            cls.get_table_class(),
            properties={'cardinality': orm.relation(
                cardinality_type,
                uselist=False,
            )},
        )
    
    def create_relation(self, characteristic):
        # Check whether the target table actually exists
        try:
            targetobj = setobject_type_registry.lookup_by_table(self.target_table)
        except KeyError:
            raise UserException("The table '" + self.target_classname + "' specified as target table does not exist")
           
        if characteristic == 'ADJACENCY_LIST':
            pass
            #self._create_adjacency_list_relation()
        elif characteristic == 'LIST':
            self._create_list_relation()
        else:
            raise Exception("Unknown relation characteristic.")

    def _create_list_relation(self):
        if self.cardinality.id == 'ONE_TO_MANY' or \
                self.cardinality.id == 'ONE_TO_ONE(FK)':
            # Create Foreign key and re-map setobject if necessary
            self.check_create_fk(
                self.target_table,
                self.source_table,
                ignoreexisting=True
            )
            return
        elif self.cardinality.id == 'MANY_TO_ONE' or \
                self.cardinality.id == 'ONE(FK)_TO_ONE':
            # Create Foreign key and re-map setobject if necessary
            self.check_create_fk(
                self.source_table,
                self.target_table,
                ignoreexisting=True
            )
            return
        elif self.cardinality.id == 'MANY_TO_MANY':
    
            if self.source_classname.lower() == self.target_classname.lower() and self.source_module.lower() == self.target_module.lower():
                raise UserException("You cannot add a relation from a plan to itself (or another plan on the same table)")
            
            self.init_xref_relation()
            
            # update session and remap source table
            getUtility(IDbUtility).Session().flush()
            sourceobj = setobject_type_registry.lookup(self.source_module, self.source_classname)
            sourceobj.sa_map()
   
 
    def _create_adjacency_list_relation(self):
        if not field_exists(self.target_table, self.foreignkeycol):
            target = setobject_type_registry.lookup_by_table(self.target_table)
            pk = target.get_primary_key_attr_name()
            col = Column(
                self.foreignkeycol,
                getattr(target.get_table_class().c, pk).type,
                ForeignKey(self.target_table + "." + pk),
            )
            col.create(target.get_table_class())
            
            # update session and remap table
            #Session().flush()
            
            # re-map user tables with newly created linkage 
            from p2.datashackle.core.models.mapping import map_tables
            map_tables(exclude_sys_tables=True)

       	    
    def check_create_fk(self, from_table_id, to_table_id, ignoreexisting=False):
        from_type = setobject_type_registry.lookup_by_table(from_table_id)        
        to_type = setobject_type_registry.lookup_by_table(to_table_id)        
        pk = to_type.get_primary_key_attr_name()
        # Now add foreign key if not existant yet
        if not field_exists(from_table_id, self.foreignkeycol):
            col = Column(
                self.foreignkeycol,
                getattr(to_type.get_table_class().c, pk).type,
                ForeignKey(to_table_id + "." + pk),
            )
            col.create(from_type.get_table_class())
           
            # The foreign key column has been newly created
            Session().flush()
            # deferred import
            from p2.datashackle.core.models.mapping import map_tables
            map_tables(exclude_sys_tables=True)
        else:
            # it exists, check whether it is what we want or something else
            fkset = getattr(from_type.get_table_class().c, self.foreignkeycol).foreign_keys
            if len(fkset) > 0:
                for fk in fkset:
                    if str(fk.column) == to_table_id + "." + pk \
                            and ignoreexisting == True:
                        return # this is what we want! fine.
                raise UserException("A relation with a similar Data Field Name but targetting the table '" + \
                    str(fk.column).split('.',1)[0] + "' already exists. Please use another Data Field Name.")
            raise UserException("The column '" + self.foreignkeycol + "' in the table '" + to_table_id + \
                "' does already exist. Please choose a unique Data Field Name that doesn't collide with existing data columns.")
   
    def init_xref_relation(self):
        # Get some vars beforehand:
        type1 = setobject_type_registry.lookup(self.source_module, self.source_classname)
        type2 = setobject_type_registry.lookup(self.target_module, self.target_classname)
        table1class = type1.get_table_class()
        table2class = type2.get_table_class()
        table1primarykey = type1.get_primary_key_attr_name()
        table2primarykey = type2.get_primary_key_attr_name()
        table1name = type1.get_table_name()
        table2name = type2.get_table_name()
        
        if self.relation.foreignkeycol.lower() == self.relation.foreignkeycol2.lower():
            raise UserException("Please choose different column names for both of the two foreign key columns")
        
        # Create/obtain xref table
        fkcol1 = Column(
            self.relation.foreignkeycol,
            getattr(table1class.c, table1primarykey).type,
            ForeignKey(table1name + "." + table1primarykey)
        )
        fkcol2 = Column(
            self.relation.foreignkeycol2,
            getattr(table2class.c, table2primarykey).type,
            ForeignKey(table2name + "." + table2primarykey)
        )
        
        mytable = Table(self.relation.xref_table, metadata, useexisting=True)
        if not mytable.exists():
            # Create table with new columns
            mytable = Table(self.relation.xref_table, metadata,
                fkcol1,
                fkcol2,
                Column('id', Integer(8), primary_key=True, autoincrement=True, default=0, nullable=False), 
                useexisting=True, mysql_engine='InnoDB')
            
            # Register table type
            setobject_table_registry.register_type('p2.datashackle.core.models.setobject_types', self.relation.xref_table, self.relation.xref_table, mytable)
            
            # Create table
            mytable.create()
            
            # Create setobject type
            create_setobject_type(self.relation.xref_table, self.relation.xref_table)
        else:
            # Alter table to have the new columns if they aren't there yet
            mytable = Table(self.relation.xref_table, metadata, autoload=True, useexisting=True)
            if hasattr(mytable.c, self.relation.foreignkeycol) != True:
                # add fkcol1
                fkcol1.create(mytable)
            if hasattr(mytable.c, self.relation.foreignkeycol2) != True:
                # add fkcol2
                fkcol2.create(mytable)
                
            # Remap xref table setobject
            setobject_type_registry.lookup_by_table(self.relation.xref_table).sa_map()
        

