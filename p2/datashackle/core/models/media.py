# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2011
# Author:  Michael Jenny <michael.jenny%40projekt-und-partner.com>

import grok

from p2.datashackle.core import model_config
from p2.datashackle.core.interfaces import *
from p2.datashackle.core.models.model import ModelBase

@model_config()
class Media(ModelBase):
   
    def generate_url(self, request, as_thumbnail):
        app = grok.getApplication()
        params = '?id=' + self.p2_id
        if as_thumbnail:
            params += '&thumbnail'
        url = grok.url(request, app, '@@media')
        url += params
        return url
