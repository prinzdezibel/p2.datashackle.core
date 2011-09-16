# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2010
# Author:  Jonas Thiem <jonas.thiem%40projekt-und-partner.com>

import grok

from zope.component import getUtility
from sqlalchemy.sql import or_,func,select

from p2.datashackle.core.app.setobjectreg import setobject_type_registry, setobject_table_registry
from p2.datashackle.core.interfaces import IDbUtility, ISimpleSQLSearch
from p2.datashackle.core.models.span.fileupload import Fileupload


class SimpleSQLSearch(grok.GlobalUtility):
    
    grok.implements(ISimpleSQLSearch)
    
    def __init__(self):
        pass
    
    def addsearchvalue(self, searchvalues, field, widget, form):
        #print "Intending to append " + field + ", " + widget + ", " + form
        for value in searchvalues:
            if value['field'] == field:
                value['forms'].append(form)
                value['widgets'].append(widget)
                return
        searchvalues.append({'field' : field, 'forms' : [form], 'widgets' : [widget]})
        #print "appended: " + str(searchvalues)
    
    def replaceoperators(self, term):
        term = term.replace("%", "\\%")
        if len(term) <= 0:
            term = "*"
        if term[0] != "*":
            term = "*" + term
        if term[-1] != "*":
            term = term + "*"
        while term.find("**") >= 0:
            term = term.replace("**", "*")
        term = term.replace("*", "%")
        return term
        
    def do(self, plan, searchterm, group, page, resultsperpage, uservars=[]):
        """ Do a search on the plan based on a generic search term and return the results.
        The results will also be associated with information about which fields actually
        matched the search query and whether there is a next page to the current one. 
        Please note this implementation is most likely SLOW and could need optimization or
        replacement at some point. """

        dbutility = getUtility(IDbUtility)
        if not dbutility.isDatabaseAvailable():
            return []
        
        # change searchterm into LIKE compatible syntax
        searchterm = self.replaceoperators(searchterm)
        
        # list to hold the search values/columns we collect from the widgets
        searchvalues = []
            
        # collect all columns based on the widgets on the form and their mapping
        for form in plan.forms.itervalues():
            for widget in form.widgets.itervalues():
                if widget.widget_type == 'relation' or \
                        widget.widget_type == 'fileupload' or \
                        widget.widget_type == 'dropdown':
                    continue
                for span in widget.spans.itervalues():
                    if hasattr(span, 'attr_name') and span.attr_name != None:
                        # We got a new column to examine.
                        if span.attr_name != 'span_value' and len(span.attr_name) > 0:
                            self.addsearchvalue(searchvalues, span.attr_name, widget.widget_identifier, form.form_identifier)
        
        # do we have some columns to search through?
        #if len(searchvalues) <= 0:
        #    return {'resultset' : None, 'searchfields' : None, 'nextpage': False} # nothing to search for!
        
        # get the table class object
        tableclass = setobject_table_registry.lookup_by_table(plan.table_identifier)
        
        # lists for composing the conditions/columns used in our query
        conditions = []
        columns = []
        
        # we always want to have the primary key column in our results
        so_type = setobject_type_registry.lookup(plan.so_module, plan.so_type)
        columns.append(getattr(tableclass.c, so_type.get_primary_key_attr_name()))
        
        # compose the search conditions based on the avilable input fields
        for value in searchvalues:
            if searchterm != '%':
                condition = getattr(tableclass.c, value['field']).like(searchterm, escape='\\')
            else:
                condition1 = getattr(tableclass.c, value['field']).like(searchterm, escape='\\')
                condition2 = (getattr(tableclass.c, value['field']) == None)
                condition = or_(condition1, condition2)
            conditions.append(condition)
            columns.append(getattr(tableclass.c, value['field']))
            columns.append(condition.label("_field_matched_" + value['field']))
        
        # compose our query
        if len(conditions) > 0:
            queryobj = select(columns).where(or_(*conditions)).offset((int(page)-1) * resultsperpage).limit(resultsperpage+1)
        else:
            queryobj = select(columns).offset((int(page)-1) * resultsperpage).limit(resultsperpage+1)
        
        # See if there is a next page to this one
        gotnextpage = False
        resultarray = []
        results = queryobj.execute()
        for result in results:
            if len(resultarray) < resultsperpage:
                resultarray.append(result)
            else:
                gotnextpage = True
        
        return {'resultset' : resultarray, 'searchfields' : searchvalues, 'nextpage' : gotnextpage}
