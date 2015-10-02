# -*- coding: utf-8 -*-

from Products.CMFCore import permissions
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory

from lmu.contenttypes.pinnwand.interfaces import IPinnwandFolder
from lmu.policy.base.browser import _AbstractLMUBaseContentView
from lmu.policy.base.browser import _FrontPageIncludeMixin
from lmu.policy.base.browser import _EntryViewMixin


def str2bool(v):
    return v is not None and v.lower() in ['true', '1']


class _AbstractPinnwandListingView(_AbstractLMUBaseContentView):

    def entries(self):
        entries = []
        if IPinnwandFolder.providedBy(self.context):
            content_filter = {
                'portal_type': 'Pinnwand Entry',
                #'review_state': ['published', 'internal-published', 'internally_published'],
            }
            if self.request.get('author'):
                content_filter['Creator'] = self.request.get('author')

            pcatalog = self.context.portal_catalog

            entries = pcatalog.searchResults(
                content_filter,
                sort_on='modified', sort_order='reverse',
                b_size=int(self.request.get('b_size', '20')),
                b_start=int(self.request.get('b_start', '0'))
            )

        return entries

    def canAdd(self):
        #current_user = api.user.get_current()
        #import ipdb; ipdb.set_trace()
        #return api.user.has_permission(permissions.AddPortalContent, user=current_user, obj=self.context)
        return api.user.has_permission(permissions.AddPortalContent, obj=self.context)


class ListingView(_AbstractPinnwandListingView):

    template = ViewPageTemplateFile('templates/listing_view.pt')

    def __call__(self):
        return self.template()


class FrontPageIncludeView(_AbstractPinnwandListingView, _FrontPageIncludeMixin):

    template = ViewPageTemplateFile('templates/frontpage_view.pt')


class EntryView(_AbstractLMUBaseContentView, _EntryViewMixin):

    template = ViewPageTemplateFile('templates/entry_view.pt')

    def __call__(self):
        return self.template()


@provider(IContextAwareDefaultFactory)
def vendorDefaultFactory(context):
    user = api.user.get_current()
    return unicode(user.fullname)


@provider(IContextAwareDefaultFactory)
def vendorEmailDefaultFactory(context):
    user = api.user.get_current()
    return unicode(user.email)
