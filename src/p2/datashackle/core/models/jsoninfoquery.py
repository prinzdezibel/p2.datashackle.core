# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2011
# Author:  Jonas Thiem <jonas.thiem%40projekt-und-partner.com>

import grok
import json
import sqlalchemy
from zope.component import getUtility

from p2.datashackle.core.interfaces import IPlan, IDbUtility, IJsonInfoQuery
from p2.datashackle.core.models.plan import Plan

class JsonInfoQuery(grok.GlobalUtility):
    """ A utility used by the JsonInfoQuery view where the actual logic for assembling the data resides. """
    grok.implements(IJsonInfoQuery)
    def get_plan_table_info(self):
        """ Dump a JSON dictionary which associates all plan identifiers with their respective table identifiers """
        if not getUtility(IDbUtility).isDatabaseAvailable():
            return json.dumps({})
        dictionary = {}
        session = getUtility(IDbUtility).Session()
        plans = session.query(Plan).all()
        for plan in plans:
            dictionary[plan.plan_identifier] = plan.table_identifier
        return json.dumps(dictionary)
