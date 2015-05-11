# -*- coding: utf-8 -*-

from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api
from plone.app.textfield.interfaces import ITransformer

from lmu.contenttypes.pinnwand.interfaces import IPinnwandFolder


def str2bool(v):
    return v is not None and v.lower() in ['true', '1']


class _AbstractPinnwandView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_memberdata(self, item):
        pmt = api.portal.get_tool(name='portal_membership')
        member_id = item.Creator()
        member = pmt.getMemberById(member_id)
        return member

    def strip_text(self, item, length=500):
        transformer = ITransformer(item)
        transformedValue = transformer(item.text, 'text/plain')
        striped_length = len(transformedValue)
        if striped_length > length:
            striped_length = transformedValue.rfind(' ', 0, length)
            transformedValue = transformedValue[:striped_length] + '...'
        return transformedValue

    def _check_permission(self, permission, item):
        pmt = api.portal.get_tool(name='portal_membership')
        return pmt.checkPermission(permission, item)


class _AbstractPinnwandListingView(_AbstractPinnwandView):

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


class FrontPageIncludeView(_AbstractPinnwandListingView):

    template = ViewPageTemplateFile('templates/frontpage_view.pt')

    def update(self):
        """
        """
        # Hide the editable-object border
        request = self.request
        request.set('disable_border', True)

    def __call__(self):
        omit = self.request.get('full')
        self.omit = not str2bool(omit)
        author = self.request.get('author')
        self.author = bool(author)
        if 'b_size' not in self.request:
            self.request.set('b_size', '3')
        if self.omit:
            REQUEST = self.context.REQUEST
            RESPONSE = REQUEST.RESPONSE
            RESPONSE.setHeader('Content-Type', 'text/xml;charset=utf-8')
        #import ipdb; ipdb.set_trace()
        return self.template()


class EntryView(_AbstractPinnwandView):

    template = ViewPageTemplateFile('templates/entry_view.pt')

    def __call__(self):
        return self.template()

    def canSeeHistory(self):
        return True

    def canEdit(self):
        return api.user.has_permission(permissions.ModifyPortalContent, obj=self.context)

    def canRemove(self):
        return api.user.has_permission(permissions.DeleteObjects, obj=self.context)

    def canLock(self):
        return api.user.has_permission(permissions.ReviewPortalContent, obj=self.context)

