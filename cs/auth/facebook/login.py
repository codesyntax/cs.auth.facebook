import json
import urlparse
import urllib
import hashlib

from zope.component import getUtility
from zope.publisher.browser import BrowserView

from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin
from Products.statusmessages.interfaces import IStatusMessage

from plone.registry.interfaces import IRegistry
from collective.beaker.interfaces import ISession

from cs.auth.facebook import FBMessageFactory as _
from cs.auth.facebook.plugin import SessionKeys
from cs.auth.facebook.interfaces import ICSFacebookPlugin


FACEBOOK_AUTH_URL         = "https://graph.facebook.com/oauth/authorize"
FACEBOOK_ACCESS_TOKEN_URL = "https://graph.facebook.com/oauth/access_token"
FACEBOOK_PROFILE_URL      = "https://graph.facebook.com/me"
FACEBOOK_PROFILE_PICTURE_URL = "https://graph.facebook.com/me/picture"
FB_AUTHENTICATION_SALT_KEY = 'cs.auth.facebook.AUTHENTICATION_SALT_KEY'
PERMISSIONS = 'email'

from logging import getLogger
log = getLogger('cs.auth.facebook')

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
        error            = self.request.form.get("error", None)
        errorReason      = self.request.form.get("error_reason", None)

        salt = hashlib.sha256().hexdigest()
        session = ISession(self.request)
        session[FB_AUTHENTICATION_SALT_KEY] = salt
        args = {
                'state': salt,
                'scope': PERMISSIONS,
                'client_id': FB_APP_ID,
                'redirect_uri': "%s/%s" % (self.context.absolute_url(), self.__name__,),
            }


        # Did we get an error back after a Facebook redirect?
        if error is not None or errorReason is not None:
            log.info(error)
            log.info(errorReason)
            IStatusMessage(self.request).add(_(u"Facebook authentication denied"), type="error")
            self.request.response.redirect(self.context.absolute_url())
            return u""

        # Check if this the status is the same...
        return_salt = self.request.form.get('status', '')
        if return_salt and return_salt != session.get(FB_AUTHENTICATION_SALT_KEY):
            IStatusMessage(self.request).add(_(u"Facebook authentication denied"), type="error")
            self.request.response.redirect(self.context.absolute_url())
            log.info('%s != %s' % (return_salt, session.get(FB_AUTHENTICATION_SALT_KEY)))
            return u""

        # If there is no code, this is probably the first request, so redirect
        # to Facebook
        if verificationCode is None:
            self.request.response.redirect(
                    "%s?%s" % (FACEBOOK_AUTH_URL, urllib.urlencode(args),)
                )

            return u""

        # If we are on the return path form Facebook,
        # exchange the return code for a token
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

        userId = profile.get('id').encode("utf-8")
        name = profile.get('name').encode("utf-8")
        email = profile.get('email', '').encode("utf-8")
        username = profile.get('username', '').encode("utf-8")
        location = profile.get('location', {}).get('name', '').encode("utf-8")

        profile_image = urllib.urlopen(
                "%s?%s" % (FACEBOOK_PROFILE_PICTURE_URL, urllib.urlencode({'access_token': accessToken}),)
            ).read()

        if not userId or not name:
            IStatusMessage(self.request).add(_(u"Insufficient information in Facebook profile"), type="error")
            self.request.response.redirect(self.context.absolute_url())
            return u""


        # Save the data in the session so that the extraction plugin can
        # authenticate the user to Plone
        session[SessionKeys.accessToken] = accessToken
        session[SessionKeys.userId]      = userId
        session[SessionKeys.userName]    = username or userId
        session[SessionKeys.fullname]    = name
        session[SessionKeys.email]       = email
        session[SessionKeys.location]    = location
        session[SessionKeys.profile_image]    = profile_image
        session.save()

        # Add user data into our plugin storage:
        acl = self.context.acl_users
        acl_plugins = acl.plugins
        ids = acl_plugins.listPluginIds(IExtractionPlugin)
        for id in ids:
            plugin = getattr(acl_plugins, id)
            if ICSFacebookPlugin.providedBy(plugin):
                user_data = plugin._storage.get(session[SessionKeys.userId], {})
                user_data['username'] = session[SessionKeys.userName]
                user_data['fullname'] = session[SessionKeys.fullname]
                user_data['email'] = session[SessionKeys.email]
                user_data['location'] = session[SessionKeys.location]
                user_data['portrait'] = session[SessionKeys.profile_image]
                plugin._storage[session[SessionKeys.userId]] = user_data


        IStatusMessage(self.request).add(_(u"Welcome. You are now logged in."), type="info")

        return_args = ''
        if self.request.get('came_from', None) is not None:
            return_args = {'came_from': self.request.get('came_from')}
            return_args = '?' + urllib.urlencode(return_args)

        self.request.response.redirect(self.context.absolute_url() + '/logged_in' + return_args)
