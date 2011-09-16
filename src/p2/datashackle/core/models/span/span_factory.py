# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2010
# Author:  Michael Jenny <michael.jenny%40projekt-und-partner.com>

from p2.datashackle.core.app.exceptions import *
from p2.datashackle.core.models.span.alphanumeric import Alphanumeric
from p2.datashackle.core.models.span.relation import Relation
from p2.datashackle.core.models.span.fileupload import Fileupload
from p2.datashackle.core.models.span.label import Label
from p2.datashackle.core.models.span.checkbox import Checkbox
from p2.datashackle.core.models.span.dropdown import Dropdown
from span import Action


def lookup_span_type(span_type):
    if str(span_type) == 'alphanumeric':
        return Alphanumeric
    elif str(span_type) == 'label':
        return Label
    elif str(span_type) == 'checkbox':
        return Checkbox
    elif str(span_type) == 'relation':
        return Relation
    elif str(span_type) == 'action':
        return Action
    elif str(span_type) == 'fileupload':
        return Fileupload
    elif str(span_type) == 'dropdown':
        return Dropdown
    else:
        raise UnspecificException("Unknown span_type: " + str(span_type))
   

def create_span(span_type_name, span_name, span_identifier):
    span_type = lookup_span_type(span_type_name)
    span = span_type(span_name, span_identifier)
    return span
