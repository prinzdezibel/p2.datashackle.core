# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2010
# Author:  Jonas Thiem <jonas.thiem%40projekt-und-partner.com>

from sqlalchemy import orm, Column, Table, String, Integer
from sqlalchemy.schema import ForeignKey
from zope.component import getUtility

from p2.datashackle.core import model_config
from p2.datashackle.core.app.exceptions import *
from p2.datashackle.core.app.setobjectreg import setobject_type_registry, setobject_table_registry
from p2.datashackle.core.sql import field_exists
from p2.datashackle.core.globals import metadata
from p2.datashackle.core.interfaces import *
from p2.datashackle.core.models.setobject_types import SetobjectType, create_setobject_type
from p2.datashackle.core.models.table import Table


@model_config(tablename='p2_linkage')
class Linkage(SetobjectType):
    source_cardinality = None
    target_cardinality = None
    is_multi_selectable = False
 
    def __init__(self, objid=None, source_module=None, source_classname=None, foreignkeycol=None,
            target_module='p2.datashackle.core.models.setobject_types', target_classname=None,
            cardinality='1:n',
            form_name='default_form',
            ref_type='dict',
            attr_name='',
            xref_table=None,
            foreignkeycol2=None
            ):
        super(Linkage, self).__init__(objid=objid)
        self.attr_name = attr_name
        self.ref_type = ref_type
        self.backref = None
        self.ref_key = None
        self.foreignkeycol = foreignkeycol
        self.form_name = form_name
        cardinalitytype = setobject_type_registry.lookup('p2.datashackle.core.models.setobject_types', 'p2_cardinality')
        self.cardinality = getUtility(IDbUtility).Session().query(cardinalitytype).filter(cardinalitytype.cardinality == cardinality).one()
        self.source_module = source_module
        self.source_classname = source_classname
        self.target_module = target_module
        self.target_classname = target_classname
        self.cascade = 'save-update, merge'
        self.post_update = False
        self.xref_table = xref_table # we only need this for n:m linkages
        self.foreignkeycol2 = foreignkeycol
        super(Linkage, self).__init__(objid=objid)
        self.init_link()
    
    @orm.reconstructor 
    def reconstruct(self):
        super(Linkage, self).reconstruct()
    
    @property
    def shareable(self):
        if self.cardinality is not None:
            if self.cardinality.cardinality == '1:1(fk)' or self.cardinality.cardinality == '1(fk):1':
                return False
        return True
        
    def check_value(self, attribute):
        value = getattr(self, attribute)
        if value is not None:
            if len(value) > 0:
                return True
        raise UserException("Linkage attribute '" + attribute + "' is not specified.")
        
    def check_if_complete(self):
        # Make sure everything is there to make up a proper linkage (will throw a UserException if not)
        
        self.check_value("source_module")
        self.check_value("source_classname")
        self.check_value("target_module")
        self.check_value("target_classname")
        self.check_value("ref_type")
        self.check_value("attr_name")
        if self.cardinality == None:
            raise UserException("Linkage attribute 'cardinality' is not specified.")
        self.check_value("foreignkeycol")
        
        self.compute_cardinality()
        if self.source_cardinality != 1 and self.target_cardinality != 1:
            self.check_value("foreignkeycol2")
            self.check_value('xref_table')
            
    def common_init(self):
        super(Linkage, self).common_init()
        self.compute_cardinality()
        
    def _foreign_key_is_on_target_side(self):
        """ Just checks if the foreign key is on the 'target' side or not (n:m will also count as 'not').
            Returns True or False accordingly."""
        if self.cardinality is None:
            raise UserException("No cardinality specified")
        cardinalitystr = self.cardinality.cardinality
        if cardinalitystr.endswith(":n") or cardinalitystr.endswith(":1(fk)"):
            return True
        return False
        
    def cardinality_list(self):
        if self.cardinality is None:
            return None
        # Obtain cardinality string value:
        cardinalitystr = self.cardinality.cardinality
        # Split it up into a list:
        cardinalitylist = cardinalitystr.replace('1(fk)', '1').replace('n', '-1').replace('m','-1').split(':', 2)
        if len(cardinalitylist) != 2:
            raise Exception("Invalid cardinality value")
        # A short consistency check:
        i = 0
        while i < 2:
            try:
                cardinalitylist[i] = int(cardinalitylist[i])
            except:
                raise Exception("Invalid cardinality value")
            if cardinalitylist[i] < 1 and cardinalitylist[i] != -1:
                raise Exception("Invalid cardinality value")
            i += 1
        return cardinalitylist

    def compute_cardinality(self):
        if self.cardinality is not None:
            cardinality = self.cardinality_list()
            self.source_cardinality = cardinality[0]
            self.target_cardinality = cardinality[1]
            if self.ref_type == 'object':
                self.is_multi_selectable = False
            else:
                if self.target_cardinality == 1:
                    self.is_multi_selectable = False
                else:
                    self.is_multi_selectable = True
            return True
        return False
    
    def is_foreignkey_on_target_table(self):
        """ Checks if the foreign key is on the target table, relative from the source table
            from where this linkage originates.
            Returns either True, False or a string "xref" for n:m relations. """
        if self.compute_cardinality() != True:
            raise Exception("Cardinality not properly set for foreignkey side check")
        if self.source_cardinality != 1 and self.target_cardinality != 1:
            return "xref"
        if self._foreign_key_is_on_target_side() == True:
            return True
        return False
    
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
        
        if self.foreignkeycol.lower() == self.foreignkeycol2.lower():
            raise UserException("Please choose different column names for both of the two foreign key columns")
        
        # Create/obtain xref table
        fkcol1 = Column(
            self.foreignkeycol,
            getattr(table1class.c, table1primarykey).type,
            ForeignKey(table1name + "." + table1primarykey)
        )
        fkcol2 = Column(
            self.foreignkeycol2,
            getattr(table2class.c, table2primarykey).type,
            ForeignKey(table2name + "." + table2primarykey)
        )
        
        mytable = Table(self.xref_table, metadata, useexisting=True)
        if not mytable.exists():
            # Create table with new columns
            mytable = Table(self.xref_table, metadata,
                fkcol1,
                fkcol2,
                Column('id', Integer(8), primary_key=True, autoincrement=True, default=0, nullable=False), 
                useexisting=True, mysql_engine='InnoDB')
            
            # Register table type
            setobject_table_registry.register_type('p2.datashackle.core.models.setobject_types', self.xref_table, self.xref_table, mytable)
            
            # Create table
            mytable.create()
            
            # Create setobject type
            create_setobject_type(self.xref_table)
        else:
            # Alter table to have the new columns if they aren't there yet
            mytable = Table(self.xref_table, metadata, autoload=True, useexisting=True)
            if hasattr(mytable.c, self.foreignkeycol) != True:
                # add fkcol1
                fkcol1.create(mytable)
            if hasattr(mytable.c, self.foreignkeycol2) != True:
                # add fkcol2
                fkcol2.create(mytable)
                
            # Remap xref table setobject
            setobject_type_registry.lookup_by_table(self.xref_table).sa_map()
        
        return
             
    def init_link(self):
        self.compute_cardinality() 
        if self.foreignkeycol is not None and len(self.foreignkeycol) > 0 and len(self.target_classname) > 0:
            # Check for a relation to the plan itself
            if self.source_classname.lower() == self.target_classname.lower() and self.source_module.lower() == self.target_module.lower():
                raise UserException("You cannot add a relation from a plan to itself (or another plan on the same table)")
            
            # Check whether the target table actually exists
            try:
                targetobj = setobject_type_registry.lookup(self.target_module, self.target_classname)
            except KeyError:
                raise UserException("The table '" + self.target_classname + "' specified as target table does not exist")
            
            foreignkey_on_target = self.is_foreignkey_on_target_table()
                        
            if foreignkey_on_target != "xref":
                # 1:n relation:
                
                if foreignkey_on_target == True:
                    # add foreignkey to other table
                    foreignkey_source_module = self.target_module # n side
                    foreignkey_source_classname = self.target_classname

                    foreignkey_target_module = self.source_module # 1 side
                    foreignkey_target_classname = self.source_classname
                else:
                    # add foreignkey to this local table (n side)
                    foreignkey_source_module = self.source_module # n side
                    foreignkey_source_classname = self.source_classname
                
                    foreignkey_target_module = self.target_module # 1 side
                    foreignkey_target_classname = self.target_classname
            else:
                # n:m relation: (with xref table
                
                # Do we have all the info?
                if self.xref_table is None or len(self.xref_table) <= 0 or self.foreignkeycol2 is None or len(self.foreignkeycol2) <= 0:
                    raise UserException("You must specify a second foreign key column and an xref table name")
                
                # Initialize our xref relation (creating the table, columns etc)
                self.init_xref_relation()
                
                # update session and remap source table
                getUtility(IDbUtility).Session().flush()
                sourceobj = setobject_type_registry.lookup(self.source_module, self.source_classname)
                sourceobj.sa_map()
                return
       	    
            # Check that foreign key column name and mapping name aren't the same
            if self.foreignkeycol.lower() == self.attr_name.lower():
                raise UserException("The name for the foreign key and the mapped attribute must be different - try using fk_ as a prefix for the foreign key column")
            
            # Create Foreign key and re-map setobject if necessary
            created = self.check_create_fk(
                foreignkey_source_module,
                foreignkey_source_classname,
                foreignkey_target_module,
                foreignkey_target_classname,
                ignoreexisting=True
            )
            if created:
                # The foreign key column has been newly created
                getUtility(IDbUtility).Session().flush()
                # deferred import
                from p2.datashackle.core.models.mapping import map_tables
                map_tables(exclude_sys_tables=True)
                
    @property
    def mode(self):
        table_name = setobject_type_registry.lookup(self.source_module, self.source_classname).get_table_name()
        if table_name in ['p2_widget', 'p2_form', 'p2_plan', 'p2_span']:
            return "non-operational"
        else:
            return "operational"
        
    def __str__(self):
        return "<" + self.__module__ + " id " + self.id + ", " + str(self.source_classname) + " -> " + str(self.target_classname) + " (Cardinality " + self.cardinality + ")>"
    
    @classmethod
    def compute_mapper_properties(cls):
        pass
    
    @classmethod
    def map_computed_properties(cls):
        pass
    
    @classmethod
    def sa_map(cls):
        table_name = cls.get_table_name()
        table = setobject_table_registry.lookup_by_table(table_name)
        cardinality_table = setobject_table_registry.lookup_by_table('p2_cardinality')
        cardinality_type = setobject_type_registry.lookup('p2.datashackle.core.models.setobject_types', 'p2_cardinality')
        # Prerequisite: p2_cardinality MUST be mapped before we can establish the 1:n relationship to p2_linkage
        cls.sa_map_dispose()
        cardinality_type.sa_map_dispose()
        orm.mapper(cardinality_type, cardinality_table)
        orm.mapper(cls,
            table,
            properties={'cardinality': orm.relation(
                cardinality_type,
                uselist=False,
            )},
        )


    def check_create_fk(self, source_module, source_classname, target_module, target_classname, ignoreexisting=False):
        """ Create a foreign key on the source table referencing the target table's primary identifier with the name self.foreignkeycol.
            This function will throw an error if the foreign key exists unless ignoreexisting is set to True.
            Returns True if a foreign key was freshly created or False if it already existed (only possible with
            ignoreexisting == True) """
        sourceobj = setobject_type_registry.lookup(source_module, source_classname)
        source_table_identifier = sourceobj.get_table_name()
        targetobj = setobject_type_registry.lookup(target_module, target_classname)
        target_table_identifier = targetobj.get_table_name()
        targetprimarykeycolumn = targetobj.get_primary_key_attr_name()
        
        # Now add foreign key if not existant yet
        if not field_exists(source_table_identifier, self.foreignkeycol):
            col = Column(
                self.foreignkeycol,
                getattr(targetobj.get_table_class().c, targetprimarykeycolumn).type,
                ForeignKey(target_table_identifier + "." + targetprimarykeycolumn),
            )
            col.create(sourceobj.get_table_class())
            return True
        else:
            # it exists, check whether it is what we want or something else
            fkset = getattr(sourceobj.get_table_class().c, self.foreignkeycol).foreign_keys
            if len(fkset) > 0:
                for fk in fkset:
                    if str(fk.column) == target_table_identifier + "." + targetprimarykeycolumn and ignoreexisting == True:
                        return False # this is what we want! fine.
                raise UserException("A relation with a similar Data Field Name but targetting the table '" + \
                    str(fk.column).split('.',1)[0] + "' already exists. Please use another Data Field Name.")
            raise UserException("The column '" + self.foreignkeycol + "' in the table '" + target_table_identifier + \
                "' does already exist. Please choose a unique Data Field Name that doesn't collide with existing data columns.")
   
    def post_order_traverse(self, mode):
        if mode == 'save':
            if self.cardinality.cardinality == '1(fk):1' or \
                    self.cardinality.cardinality == 'n:1':
                self.ref_type= 'object' 
       
