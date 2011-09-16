# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2011
# Author:  Michael Jenny <michael.jenny%40projekt-und-partner.com>

import grok

from p2.datashackle.core.interfaces import *
from p2.datashackle.core.models.setobject_types import SetobjectType
from p2.datashackle.core.app.directive import tablename

class Media(SetobjectType):
    tablename('p2_media')
   
    def generate_url(self, request, as_thumbnail):
        app = grok.getApplication()
        params = '?id=' + self.p2_id
        if as_thumbnail:
            params += '&thumbnail'
        url = grok.url(request, app, '@@media')
        url += params
        return url
