# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2011
# Author:  Jonas Thiem <jonas.thiem%40projekt-und-partner.com>

from zope.interface import Interface
from zope.location.interfaces import ILocation

        

class IDbUtility(Interface):
    """A utility that provides sqlalchemy sessions."""
    
class ISimpleSQLSearch(Interface):
    """A search tool that allows to query a relational data set with the help of a provided plan"""


class IRelationalDatabaseOpened(Interface):
    """This event will allow you to run code on a newly opened relational database."""


class IRelation(Interface):
    pass

