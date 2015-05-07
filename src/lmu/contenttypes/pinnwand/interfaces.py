# -*- coding: utf-8 -*-

#from plone.directives import dexterity
from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable

#from plone.supermodel import model
from plone.theme.interfaces import IDefaultPloneLayer

from zope import schema

#from zope.interface import Attribute
#from zope.interface import Interface

from lmu.contenttypes.pinnwand import MessageFactory as _


class IPinnwandFolder(form.Schema, IImageScaleTraversable):
    """
    Folder for Pinnwand Entries with special views and restrictions
    """
    form.model("models/pinnwand_folder.xml")


class IPinnwandEntry(form.Schema, IImageScaleTraversable):
    """
    Pinnwand Entry with folder support for files and images
    """
    form.model("models/pinnwand_entry.xml")


class IPinnwandLayer(IDefaultPloneLayer):
    """ A layer specific to this product.
        Is registered using browserlayer.xml
    """


class IPinnwandReportForm(form.Schema):

    name = schema.TextLine(
        title=_(u"Name of Reporter"),
        description=_(u"""Name of the Person reporting this issue,
will be filled by System.""")
    )

    url = schema.URI(
        title=_(u"Reported URL"),
        description=_(u"The Reported URL of the Pinnwand Entry.")
    )

    message = schema.Text(
        title=_(u"Report Message"),
        description=_(u"Please describe why you report this Pinnwand Entry")
    )
