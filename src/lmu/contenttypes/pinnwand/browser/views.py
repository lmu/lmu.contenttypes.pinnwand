# -*- coding: utf-8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from datetime import datetime
from datetime import timedelta
from plone import api
from plone.dexterity.browser import add
from plone.dexterity.browser import edit
from plone.dexterity.events import EditFinishedEvent
from z3c.form import button as button_decorator
from zope.event import notify

from z3c.form.validator import SimpleFieldValidator
from zope.interface.exceptions import Invalid
from zope.interface import provider
from plone.protect.interfaces import IDisableCSRFProtection
from plone.supermodel.interfaces import IDefaultFactory
#from zope.schema.interfaces import IContextAwareDefaultFactorying
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import alsoProvides

from lmu.policy.base.browser.content import _AbstractLMUBaseContentView
from lmu.policy.base.browser.content import _EntryViewMixin
from lmu.policy.base.browser.content import RichTextWidgetConfig
from lmu.policy.base.browser.content import formHelper
from lmu.policy.base.browser.content_listing import _AbstractLMUBaseListingView
from lmu.policy.base.browser.content_listing import _FrontPageIncludeMixin
from lmu.policy.base.browser.utils import isDBReadOnly as uIsDBReadOnly
from lmu.policy.base.controlpanel import ILMUSettings

from lmu.contenttypes.blog import MESSAGE_FACTORY as _  # XXX move translations
from lmu.contenttypes.pinnwand.interfaces import IPinnwandFolder

from logging import getLogger

log = getLogger(__name__)


def str2bool(v):
    return v is not None and v.lower() in ['true', '1']


class AutoDeleteView(BrowserView):

    def __init__(self, context, request):
        super(AutoDeleteView, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        with api.env.adopt_roles(['Manager']):
            context = self.context
            registry = getUtility(IRegistry)
            lmu_settings = registry.forInterface(ILMUSettings)
            del_delta = timedelta(days=int(lmu_settings.del_timedelta))
            if context.del_timedelta:
                del_delta = timedelta(days=int(context.del_timedelta))
            del_time = datetime.today() - del_delta
            entries = api.content.find(
                context=context,
                portal_type='Pinnwand Entry'
                )
            deleted_objs = []
            return_info = ''
            for entry in entries:
                obj = entry.getObject()
                if obj.expires < del_time:
                    deleted_objs.append({
                        'title': obj.title,
                        'url': obj.absolute_url(),
                        'expires_date': obj.expires
                    })
                    return_info += '* Delete Pinnwand Entry: "{title}" at {url} which has expired on {expires_date}\n'.format(title=obj.title, url= obj.absolute_url(), expires_date=obj.expires.strftime('%d.%m.%Y'))
                    log.info(
                        'Delete Pinnwand Entry "%s" as it has expired on %s',
                        obj.title, obj.expires.strftime('%d.%m.%Y')
                    )
                    api.content.delete(obj=obj)
            if not deleted_objs:
                return 'No Pinnwand Entries deleted, no Entry has expired before {date}'.format(date=del_time.strftime('%d.%m.%Y'))
            else:
                return_info = '{num} Pinnwand Entries have been deleted, due to expiring before {date}\n'.format(num=len(deleted_objs), date=del_time.strftime('%d.%m.%Y')) + return_info
            return return_info


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


class FrontPageIncludeView(
        _AbstractLMUBaseListingView,
        _FrontPageIncludeMixin):

    template = ViewPageTemplateFile('templates/frontpage_view.pt')

    DEFAULT_LIMIT = 3
    portal_type = 'Pinnwand Entry'
    container_interface = IPinnwandFolder
    sort_on = 'modified'


class EntryView(_AbstractLMUBaseContentView, _EntryViewMixin):

    template = ViewPageTemplateFile('templates/entry_view.pt')

    def __call__(self):
        return self.template()


class PinnwandEntryAddForm(add.DefaultAddForm):
    template = ViewPageTemplateFile('templates/pinnwand_entry_add.pt')

    portal_type = 'Pinnwand Entry'
    label = None
    description = _(u'Geben Sie zunächst die Kategorie, den Titel und Text Ihres Pinnwand-Eintrags an und klicken Sie auf "Weiter". Danach können Sie Bilder und andere Dateien hinzufügen.')

    def update(self):
        self.updateWidgets()
        text = self.schema.get('text')
        text.widget = RichTextWidgetConfig()

        formHelper(self,
                   fields_to_show=[],
                   fields_to_input=['title', 'description', 'expires'],
                   fields_to_hide=['IPublication.effective',
                                   'IPublication.expires', ],
                   fields_to_omit=['IVersionable.changeNote', ])

        buttons = self.buttons
        for button in buttons.values():
            # button.klass = u' button large round'
            if button.__name__ == 'save':
                button.title = _(u'Next')

        return super(PinnwandEntryAddForm, self).update()

    @button_decorator.buttonAndHandler(_('Save'), name='save')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True

    def isDBReadOnly(self):
        return uIsDBReadOnly()


class PinnwandEntryAddView(add.DefaultAddView):
    form = PinnwandEntryAddForm
    widgets = form.widgets
    groups = form.groups


class PinnwandEntryEditForm(edit.DefaultEditForm):

    template = ViewPageTemplateFile('templates/pinnwand_entry_edit.pt')

    description = _(u'Bearbeiten Sie Ihren Pinnwand-Eintrag. Klicken Sie anschließend auf "Vorschau", um die Eingaben zu überprüfen und den Pinnwand-Eintrag zu veröffentlichen.')

    portal_type = 'Pinnwand Entry'

    def __call__(self):
        self.updateWidgets()

        text = self.schema.get('text')
        text.widget = RichTextWidgetConfig()

        formHelper(self,
                   fields_to_show=[],
                   fields_to_input=['title', 'description', 'expires'],
                   fields_to_hide=['IPublication.effective',
                                   'IPublication.expires', ],
                   fields_to_omit=['IVersionable.changeNote', ])

        buttons = self.buttons

        for button in buttons.values():
            if button.__name__ == 'save':
                button.title = _(u'Preview')

        return super(PinnwandEntryEditForm, self).__call__()

    def isDBReadOnly(self):
        return uIsDBReadOnly()

    @button_decorator.buttonAndHandler(_(u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        self.request.response.redirect(self.nextURL())
        notify(EditFinishedEvent(self.context))


@provider(IDefaultFactory)
def vendorDefaultFactory():
    user = api.user.get_current()
    return safe_unicode(user.getProperty('fullname'))


@provider(IDefaultFactory)
def vendorEmailDefaultFactory():
    user = api.user.get_current()
    return unicode(user.getProperty('email'))


@provider(IDefaultFactory)
def expiresDefaultFactory():
    default_date = datetime.now() + timedelta(15)
    return datetime(default_date.year, default_date.month, default_date.day)


class ExpiresValidator(SimpleFieldValidator):

    def validate(self, value):
        super(ExpiresValidator, self).validate(value)
        if not value < datetime.now() + timedelta(186):
            raise Invalid("Eintrag muss in spätestens 6 Monaten ablaufen")
