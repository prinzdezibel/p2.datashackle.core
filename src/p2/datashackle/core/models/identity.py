# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2010
# Author:  Michael Jenny <michael.jenny%40projekt-und-partner.com>

import random


def generate_random_identifier():
    n_id = random.randint(0, 100000000)
    id = "%010d" % n_id
    return id
