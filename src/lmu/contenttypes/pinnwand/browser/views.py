# -*- coding: utf-8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from datetime import datetime
from datetime import timedelta
from plone import api
from plone.dexterity.browser import add
from plone.dexterity.browser import edit
from z3c.form.validator import SimpleFieldValidator
from zope.interface.exceptions import Invalid
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory

from lmu.policy.base.browser.content import _AbstractLMUBaseContentView
from lmu.policy.base.browser.content import _EntryViewMixin
from lmu.policy.base.browser.content import RichTextWidgetConfig
from lmu.policy.base.browser.content import formHelper
from lmu.policy.base.browser.content_listing import _AbstractLMUBaseListingView
from lmu.policy.base.browser.content_listing import _FrontPageIncludeMixin

from lmu.contenttypes.blog import MESSAGE_FACTORY as _  # XXX move translations
from lmu.contenttypes.pinnwand.interfaces import IPinnwandFolder


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
            #button.klass = u' button large round'
            if button.__name__ == 'save':
                button.title = _(u'Next')

        return super(PinnwandEntryAddForm, self).update()


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


@provider(IContextAwareDefaultFactory)
def vendorDefaultFactory(context):
    user = api.user.get_current()
    return unicode(user.getProperty('fullname'))


@provider(IContextAwareDefaultFactory)
def vendorEmailDefaultFactory(context):
    user = api.user.get_current()
    return unicode(user.getProperty('email'))


@provider(IContextAwareDefaultFactory)
def expiresDefaultFactory(context):
    default_date = datetime.now() + timedelta(15)
    return datetime(default_date.year, default_date.month, default_date.day)


class ExpiresValidator(SimpleFieldValidator):

    def validate(self, value):
        super(ExpiresValidator, self).validate(value)
        if not value < datetime.now() + timedelta(186):
            raise Invalid("Eintrag muss in spätestens 6 Monaten ablaufen")
