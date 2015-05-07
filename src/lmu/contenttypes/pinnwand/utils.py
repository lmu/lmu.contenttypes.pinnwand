# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import safe_unicode
#from plone.app.contenttypes.indexer import _unicode_save_string_concat(*args)
from plone.indexer.decorator import indexer

from lmu.contenttypes.pinnwand.interfaces import IPinnwandFolder
from lmu.contenttypes.pinnwand.interfaces import IPinnwandEntry


@indexer(IPinnwandFolder)
def SearchableText_pinnwandfolder(obj):

    return u" ".join((
        safe_unicode(obj.id),
        safe_unicode(obj.title) or u"",
        safe_unicode(obj.description) or u"",
    ))


@indexer(IPinnwandEntry)
def SearchableText_pinnwandentry(obj):
    return u" ".join((
        safe_unicode(obj.id),
        safe_unicode(obj.title) or u"",
        safe_unicode(obj.description) or u"",
        safe_unicode(obj.text.output) or u"",
    ))
