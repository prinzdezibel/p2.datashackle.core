# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2011
# Author:  Jonas Thiem <jonas.thiem%40projekt-und-partner.com>

from zope.interface import Interface
from zope.location.interfaces import ILocation

        
class ILocationProvider(Interface):
    """Provides means to make a p2.plan instance locatable to address it by URL. """

class IDbUtility(Interface):
    """A utility that provides sqlalchemy sessions."""
    
class ISimpleSQLSearch(Interface):
    """A search tool that allows to query a relational data set with the help of a provided plan"""


class IRelationalDatabaseOpened(Interface):
    """This event will allow you to run code on a newly opened relational database."""

class IPlan(Interface):
    """Represents different views onto objects. The objects has different properties.
    The ´Plan´ does not only represent the values of the objects itself
    (the instances), but also the blueprint (e.g. which properties does it have)
    of the object (the type). The ´Plan's´ different views are manifested
    through a collection of ´Forms´ it holds. The ´Plan´ is wired with a table
    in a relational database.
    """

class IFormType(Interface):
    """IFormType represents a visualization of a table record as form.
    Represents a ´Form´ in "type mode" that works on the fields (or a subset) of
    a table in the relational database. A ´Form´ is a domain thing that is
    composed out of ´Widgets´. In "design mode", the form may be changed
    in layout and function by authorized users. E.g. new fields may be added to the form.
    In "setobject mode", new instances of
    the form may be created which can be filled out by the user which are eventually saved in db.
    """

class IRelation(Interface):
    pass

class IWidgetType(Interface):
    pass


class ISpanType(Interface):
    pass

class IJsonInfoQuery(Interface):
    """ Allows to query for JSON info objects that can be returned to a javascript client through Ajax.
    So far, this is used to gather info about the table identifiers for all the plans in the application. """
