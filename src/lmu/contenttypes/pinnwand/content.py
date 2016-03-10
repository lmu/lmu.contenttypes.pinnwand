# -*- coding: utf-8 -*-

from datetime import datetime

from Products.CMFPlone.interfaces.syndication import ISyndicatable

from Products.statusmessages.interfaces import IStatusMessage

#from plone.dexterity.content import Item
from plone.dexterity.content import Container

#from plone.app.contenttypes.behaviors.leadimage import ILeadImage
from plone.directives import form

from zope.interface import implements

from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from z3c.form import button

from lmu.contenttypes.pinnwand.interfaces import IPinnwandFolder
from lmu.contenttypes.pinnwand.interfaces import IPinnwandEntry
from lmu.contenttypes.pinnwand.interfaces import IPinnwandReportForm

from lmu.contenttypes.pinnwand import MessageFactory as _
from lmu.policy.base.content import LMUBaseContent


pinnwand_entry_types_vocabulary = SimpleVocabulary([
    SimpleTerm(token='suche', value=u'Suche', title=u'Suche'),
    SimpleTerm(token='biete', value=u'Biete', title=u'Biete')
])


class PinnwandFolder(Container):
    implements(IPinnwandFolder, ISyndicatable)


class PinnwandEntry(LMUBaseContent):
    implements(IPinnwandEntry)

    def isExpired(self):
        return self.expires < datetime.now()


class PinnwandReportForm(form.SchemaForm):
    implements(IPinnwandReportForm)

    schema = IPinnwandReportForm
    ignoreContext = True

    label = _(u"Report a Pinnwand Entry")
    description = _(u"Report a Pinnwand Entry that violates the Pinnwand rules.")

    @button.buttonAndHandler(_(u"Report Pinnwand Entry"), name="report")
    def handle_report(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # Do something with valid data here

        # Set status on this form page
        # (this status message is not bind to the session
        # and does not go thru redirects)
        self.status = _(u"Thank you for your Report. E-Mail send to Webmaster.")
        IStatusMessage(self.request).addStatusMessage(
            _(u"Thank you for your Report. E-Mail send to Webmaster."),
            'info')
        redirect_url = self.context.absolute_url()
        self.request.response.redirect(redirect_url)

    @button.buttonAndHandler(u"Cancel")
    def handle_cancel(self, action):
        """User cancelled. Redirect back to the front page.
        """
        IStatusMessage(self.request).addStatusMessage(
            "Notting Reported",
            'info')
        redirect_url = self.context.absolute_url()
        self.request.response.redirect(redirect_url)

    def updateActions(self):
        super(PinnwandReportForm, self).updateActions()
        self.actions['cancel'].addClass("button")
        self.actions['report'].addClass("button")

#    def updateFields(self):
#        super(PinnwandReportForm, self).updateFields()
#        self.fields['url'].value = self.context.absolute_url()
