from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class LoginViewlet(ViewletBase):
    index = ViewPageTemplateFile("templates/facebooklogin_viewlet.pt")

    def update(self):
        super(LoginViewlet, self).update()
        registry = getUtility(IRegistry)
        self.fb_app_ip = registry.get(
            'cs.auth.facebook.controlpanel.IFacebookloginSettings.fb_app_id')

    def render(self):
        if self.portal_state.anonymous():
            return self.index()
        return u""
    