from cs.auth.facebook import FBMessageFactory as _
from plone.app.registry.browser.controlpanel import (
    ControlPanelFormWrapper, 
    RegistryEditForm,
)
from plone.z3cform import layout
from zope import schema
from zope.interface import Interface


class IFacebookloginSettings(Interface):
    fb_app_id = schema.TextLine(title=_(u'App ID/API Key'),
                                description=_(u'The App ID/API Key you got when creating the app at https://developers.facebook.com/apps'))
    fb_app_secret = schema.TextLine(title=_(u'App Secret'),
                                    description=_(u'The App Secret Key you got when creating the app at https://developers.facebook.com/apps'))


class FacebookloginControlPanelForm(RegistryEditForm):
    schema = IFacebookloginSettings

FacebookloginControlPanelView = layout.wrap_form(FacebookloginControlPanelForm, ControlPanelFormWrapper)
FacebookloginControlPanelView.label = _(u"Facebooklogin Settings")
