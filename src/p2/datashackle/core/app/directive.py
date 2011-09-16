# -*- coding: utf-8 -*-
# Copyright (C) 2011, projekt-und-partner.com
# Author: Michael Jenny

import martian


class tablename(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE

class maporder(martian.Directive):
    """Specifies the order in which the tables are mapped. Default value is 1. Bigger value means later mapping.
    The directive is optional.
    """
    scope = martian.CLASS
    store = martian.ONCE
