# -*- coding: utf-8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory

from lmu.contenttypes.blog import MESSAGE_FACTORY as _  # XXX move translations
from lmu.contenttypes.pinnwand.interfaces import IPinnwandFolder
from lmu.policy.base.browser import _AbstractLMUBaseContentEditForm
from lmu.policy.base.browser import _AbstractLMUBaseContentView
from lmu.policy.base.browser import _AbstractLMUBaseListingView
from lmu.policy.base.browser import _FrontPageIncludeMixin
from lmu.policy.base.browser import _EntryViewMixin


def str2bool(v):
    return v is not None and v.lower() in ['true', '1']


class ListingView(_AbstractLMUBaseListingView):

    template = ViewPageTemplateFile('templates/listing_view.pt')

    DEFAULT_LIMIT = 20
    portal_type = 'Pinnwand Entry'
    container_interface = IPinnwandFolder
    sort_on = 'modified'

    def __init__(self, context, request):
        super(ListingView, self).__init__(context, request)

        if self.request.get('author'):
            self.content_filter['Creator'] = self.request.get('author')

    def __call__(self):
        return self.template()


class FrontPageIncludeView(_AbstractLMUBaseListingView, _FrontPageIncludeMixin):

    template = ViewPageTemplateFile('templates/frontpage_view.pt')

    DEFAULT_LIMIT = 20
    portal_type = 'Pinnwand Entry'
    container_interface = IPinnwandFolder
    sort_on = 'modified'


class EntryView(_AbstractLMUBaseContentView, _EntryViewMixin):

    template = ViewPageTemplateFile('templates/entry_view.pt')

    def __call__(self):
        return self.template()


class PinnwandEntryEditForm(_AbstractLMUBaseContentEditForm):
    template = ViewPageTemplateFile('templates/pinnwand_entry_edit.pt')

    description = _(u'Bearbeiten Sie Ihren Pinnwand-Beitrag. Klicken Sie anschließend auf "Vorschau", um die Eingaben zu überprüfen und den Blog-Eintrag zu veröffentlichen.')

    portal_type = 'Pinnwand Entry'


@provider(IContextAwareDefaultFactory)
def vendorDefaultFactory(context):
    user = api.user.get_current()
    return unicode(user.fullname)


@provider(IContextAwareDefaultFactory)
def vendorEmailDefaultFactory(context):
    user = api.user.get_current()
    return unicode(user.email)
