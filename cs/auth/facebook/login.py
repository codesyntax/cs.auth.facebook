from zope.component import getUtility
from plone.registry.interfaces import IRegistry
import json
import urlparse
import urllib

from zope.publisher.browser import BrowserView

from collective.beaker.interfaces import ISession

from Products.statusmessages.interfaces import IStatusMessage

from cs.auth.facebook import FBMessageFactory as _
from cs.auth.facebook.plugin import SessionKeys

FACEBOOK_AUTH_URL         = "https://graph.facebook.com/oauth/authorize"
FACEBOOK_ACCESS_TOKEN_URL = "https://graph.facebook.com/oauth/access_token"
FACEBOOK_PROFILE_URL      = "https://graph.facebook.com/me"

class FacebookLogin(BrowserView):
    """This view implements the Facebook OAuth 2.0 login protocol.

    The user may access the view via a link in an action or elsewhere. He
    will then be immediately redirected to Facebook, which will ask him to
    authorize this as an application.
    
    Assuming that works, Facebook will redirect the user back to this same
    view, with a code in the request.
    """
    
    def __call__(self):
        registry = getUtility(IRegistry)
        FB_APP_ID = registry.get('cs.auth.facebook.controlpanel.IFacebookloginSettings.fb_app_id').encode()
        FB_APP_SECRET = registry.get('cs.auth.facebook.controlpanel.IFacebookloginSettings.fb_app_secret').encode()

        verificationCode = self.request.form.get("code", None)
        errorReason      = self.request.form.get("error_reason", None)
        
        args = {
                'client_id': FB_APP_ID,
                'redirect_uri': "%s/%s" % (self.context.absolute_url(), self.__name__,),
            }

        
        # Did we get an error back after a Facebook redirect?
        
        if errorReason is not None:
            IStatusMessage(self.request).add(_(u"Facebook authentication denied"), type="error")
            self.request.response.redirect(self.context.absolute_url())
            return u""
        
        # If there is no code, this is probably the first request, so redirect
        # to Facebook
        
        if verificationCode is None:
            
            self.request.response.redirect(
                    "%s?%s" % (FACEBOOK_AUTH_URL, urllib.urlencode(args),)
                )
            
            return u""
        
        # If we are on the return path form Facebook, exchange the return code
        # for a token
        args["client_secret"] = FB_APP_SECRET
        args["code"] = verificationCode
        
        response = urlparse.parse_qs(urllib.urlopen(
                "%s?%s" % (FACEBOOK_ACCESS_TOKEN_URL, urllib.urlencode(args),)
            ).read())
        
        # Load the profile using the access token we just received
        accessToken = response["access_token"][-1]
        
        profile = json.load(urllib.urlopen(
                "%s?%s" % (FACEBOOK_PROFILE_URL, urllib.urlencode({'access_token': accessToken}),)
            ))
        
        userId = profile.get('id')
        name = profile.get('name')
        
        if not userId or not name:
            IStatusMessage(self.request).add(_(u"Insufficient information in Facebook profile"), type="error")
            self.request.response.redirect(self.context.absolute_url())
            return u""
        
        # Save the data in the session so that the extraction plugin can 
        # authenticate the user to Plone
        
        session = ISession(self.request)

        session[SessionKeys.accessToken] = accessToken
        session[SessionKeys.userId]      = userId
        session[SessionKeys.userName]    = userId
        session[SessionKeys.fullname]    = name
        
        session.save()
        
        IStatusMessage(self.request).add(_(u"Welcome. You are now logged in."), type="info")
        self.request.response.redirect(self.context.absolute_url() + '/logged_in')