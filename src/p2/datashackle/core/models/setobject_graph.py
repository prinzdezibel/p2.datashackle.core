# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2010
# Author:  Michael Jenny <michael.jenny%40projekt-und-partner.com>

import logging

from lxml import etree
from lxml.etree import ElementTree
from zope.component import getUtility
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import make_transient
from zope.component import getMultiAdapter, queryMultiAdapter

from p2.datashackle.core.interfaces import *
from p2.datashackle.core.app.exceptions import SetobjectGraphException, UserException, UnspecificException
from p2.datashackle.core.app.setobjectreg import setobject_type_registry
from p2.datashackle.core.interfaces import IDbUtility
from p2.datashackle.core.models.media import Media
from p2.datashackle.core.models.span.span import SpanType
from p2.datashackle.core.models.span.alphanumeric import Alphanumeric


class SetobjectGraph(object):
    
    def __init__(self, plan_identifier, request, raw_xml):
        self.plan_identifier = plan_identifier
        self.session = getUtility(IDbUtility).Session()
        # deferred import
        from p2.datashackle.core.models.plan import Plan
        plan = self.session.query(Plan).filter_by(plan_identifier=self.plan_identifier).one()
        self.table_identifier = plan.table_identifier
        self.request = request
        self.xml_root = etree.fromstring(raw_xml)
 
    def save(self):
        self.mode = 'save'
        try:
            self.dfs_main(self.xml_root, None, None)
            self.session.commit()
        except Exception:
            self.session.rollback()
            self.session.close()
            self.session = getUtility(IDbUtility).Session()
            raise           

    def update_collections(self):
        self._each_collection(self.xml_root, None)

    def _each_collection(self, node, setobject):
        if node.tag == 'obj':
            module = node.get('module')
            typename = node.get('type')
            so_type = setobject_type_registry.lookup(module, typename)
            objid = node.get('objid')
            setobject = self.session.query(so_type).get(objid)
            assert(setobject != None)
        for child in node:
            self._each_collection(child, setobject)
        # post order processing
        if node.tag == 'obj':
            self.process_collection_ids(node, setobject)

    def link(self, collection_id, module, classname, setobject_id, linked):
        self.mode = 'link'
        def callback(coll_node):
            if coll_node.get('linkage_id') == collection_id:
                # Check if setobject is already in xml
                found = False
                for child in coll_node:
                    if child.get('objid') == setobject_id:
                        found = True
                        break
                if not found:
                    if __debug__:
                        so_type = setobject_type_registry.lookup(module, classname)
                        assert(self.session.query(so_type).get(setobject_id) != None)
                    obj = etree.Element("obj")
                    # The setobject MUST already be present in sqlalchemy session. 
                    # Through action 'save' it is later queried again.
                    obj.set('action', 'save')
                    obj.set('objid', setobject_id)
                    obj.set('linked', linked)
                    obj.set('module', module)
                    obj.set('type', classname)
                    coll_node.append(obj)
        try:
            self.dfs_main(self.xml_root, None, callback)
        except:
            # we don't want to have the incompletely filled in graph objects hanging around
            self.session.rollback()
            self.session.close()
            raise

    def dfs_main(self, node, setobject, callback, parent_setobject=None):
        descend = True
        preceding_setobject = setobject
        if node.tag == 'prop':
            attribute = node.get('name')
            value = node.text
            span_identifier = node.get('span_identifier')
            if span_identifier is not None:
                session = getUtility(IDbUtility).Session()
                span_type = setobject_type_registry.lookup('p2.datashackle.core.models.span.span', 'SpanType')
                span = session.query(span_type).get(span_identifier)
                assert(span != None)
                span.onbefore_set_payload_attribute(setobject, attribute, value, self.mode)
            setobject.set_attribute(attribute, value, self.mode)
        elif node.tag == 'obj':
            # Method sets up a processing scope which results
            # in new assignment of setobject.
            setobject, descend = self.process_object(node, parent_setobject)
        elif node.tag == 'coll':
            if self.mode == 'link':
                callback(node)
            attr_name = node.get('attr_name')
            linkage = setobject.collections[attr_name]['linkage']
            reftype = linkage.ref_type
            if setobject.action != 'new' and reftype == 'object':
                # Set the attribute to None. If it's still linked, it will be done
                # so in do_linkage, but if not anymore, the attribute is deleted here.
                setattr(setobject, attr_name, None)
        elif node.tag == 'root':
            pass
        else:
            # Unknown/invalid node.
            raise SetobjectGraphException("Unknown node '" + node.tag + "'")
           
        if descend:
            # Traverse deeper into graph
            for child in node:
                self.dfs_main(child, setobject, callback, preceding_setobject)
       
        self.post_order_processing(node, setobject, preceding_setobject)
    
    def process_object(self, node, parent_setobject):
        action = node.get('action')
        module = node.get('module')
        typename = node.get('type')
        so_type = setobject_type_registry.lookup(module, typename)
        objid = node.get('objid')
        linked = node.get('linked')

        setobject = None
        if action == 'new' and node.getparent().tag == 'coll':
            attr_name = node.getparent().get('attr_name')
            linkage = parent_setobject.collections[attr_name]['linkage']
            reftype = linkage.ref_type
            if reftype == 'object':
                if linked == 'true' and getattr(parent_setobject, attr_name, None) != None:
                    setobject = getattr(parent_setobject, attr_name)
                    setobject.id = objid
            else:
                refkey = linkage.ref_key
                coll = getattr(parent_setobject, attr_name)
                key = None
                if refkey == None:
                    key = node.get('objid')
                else:
                    for prop in node:
                        if prop.get('name') == refkey:
                            key = prop.text
                            break;
                    assert(key != None)
                if key in coll:
                    setobject = coll[key]
                    setobject.id = objid
        if setobject == None:
            if action == 'save':
                setobject = self.session.query(so_type).filter(so_type.get_primary_key_attr() == objid).one()
                self.session.add(setobject)
                self.session.flush()
            elif action == 'new':
                assert(self.session.query(so_type).get(objid) is None)
                setobject = so_type(objid=objid)
                self.session.add(setobject)
                self.session.flush()
            elif action == 'delete':
                setobject = self.session.query(so_type).filter(so_type.get_primary_key_attr() == objid).one()
                # Actual deletion is performed as post order step as it may be necessary
                # to clear linkages prior deleting the object.
                setobject = self.session.query(so_type).filter(so_type.get_primary_key_attr() == objid).one()
            else:
                raise SetobjectGraphException("Invalid action '" + action + "' for setobject", node.get('objid'))
        
        self.do_linkage(node, setobject, parent_setobject)
        if action != 'delete':
            # do_linkage wipes out backrefs and such, this confuses e.g. the widget on initialization
            setobject.pre_order_traverse()
        
        setobject = self.session.query(so_type).get(objid)
        assert(setobject != None)
        
        if action == 'delete':
            # Don't need to traverse deeper in tree.
            descend = False
        else:
            descend = True
        return setobject, descend
        
    def do_linkage(self, node, setobject, parent_setobject):
        linked = node.get('linked')
        if linked != None:
            if node.tag != 'obj': raise UnspecificException("Linked node must be of type obj.")
            collection_node = node.getparent() 
            if collection_node.tag != 'coll':
                # Parent is not of type coll.
                # Ignore it.
                return
    
            attr_name = collection_node.get('attr_name')
            span_identifier = collection_node.get('span_identifier')
            linkage = parent_setobject.collections[attr_name]['linkage']
            refkey = linkage.ref_key
            reftype = linkage.ref_type
 
            if reftype == 'object':
                if linked == 'true':
                    span_identifier = node.get('span_identifier')
                    if span_identifier is not None:
                        session = getUtility(IDbUtility).Session()
                        span_type = setobject_type_registry.lookup('p2.datashackle.core.models.span.span', 'SpanType')
                        span = session.query(span_type).get(span_identifier)
                        span.onbefore_set_payload_attribute(
                            setobject=parent_setobject,
                            attribute=attr_name,
                            value=setobject,
                            mode=self.mode
                        )
                    parent_setobject.set_attribute(
                        attribute=attr_name,
                        value=setobject,    
                        mode=self.mode
                    )
                    #setattr(parent_setobject, attr_name, setobject)
            else:
                coll = getattr(parent_setobject, attr_name)
                # Refkey: If there's a refkey the value of the key is searched within the object's properties.
                # If there's no refkey specified, we use the objid itself.
                key = None
                if refkey == None:
                    key = node.get('objid')
                else:
                    key = getattr(setobject, refkey)
                # Do actual linkage
                if linked == 'true':
                    coll[key] = setobject
                elif linked == 'false':
                    if key in coll:
                        del coll[key]
                else:
                    raise UnspecificException("Invalid link state.")
            # This flush is necessary. Otherwise it seems that if another reference to THIS object is
            # subsquently deleted via del coll[key], this linkage will not be persisted.
            self.session.flush()
    
    def post_order_processing(self, node, setobject, parent_setobject):
        if node.tag == 'root':
            return
        if node.tag == 'obj':
            self.do_linkage(node, setobject, parent_setobject)
        action = node.get('action') 
        if node.tag == 'coll' and node.get('span_identifier') != None:
            span_identifier = node.get('span_identifier')
            session = getUtility(IDbUtility).Session()
            span_type = setobject_type_registry.lookup('p2.datashackle.core.models.span.span', 'SpanType')
            span = session.query(span_type).get(span_identifier)
            span.onbefore_post_order_traverse(setobject, self.mode)
        elif node.tag == 'obj' and node.get('action') != 'delete':
            setobject.post_order_traverse(self.mode)   
        if node.tag == 'obj':
            if self.mode == 'save' and action == 'delete':
                self.session.delete(setobject)
            else:
                self.process_collection_ids(node, setobject)
        
    def process_collection_ids(self, node, setobject):
        # Restore the collection ids from the graph objects
        assert(setobject is not None)
        for child in node:
            if child.tag == 'coll':
                attr_name = child.get('attr_name')
                setobject.collections[attr_name]['collection_id'] = child.get('linkage_id')
        

