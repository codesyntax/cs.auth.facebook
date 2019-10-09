# -*- coding: utf-8 -*-
import hashlib
import json
import urllib
from logging import getLogger

from cs.auth.facebook import FBMessageFactory as _
from cs.auth.facebook.interfaces import ICSFacebookPlugin
from cs.auth.facebook.plugin import SessionKeys
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getUtility
from zope.publisher.browser import BrowserView

FACEBOOK_AUTH_URL = "https://www.facebook.com/v4.0/dialog/oauth"
FACEBOOK_ACCESS_TOKEN_URL = "https://graph.facebook.com/v4.0/oauth/access_token"
FACEBOOK_PROFILE_URL = "https://graph.facebook.com/me"
FACEBOOK_PROFILE_PICTURE_URL = "https://graph.facebook.com/me/picture"
FB_AUTHENTICATION_SALT_KEY = 'cs.auth.facebook.AUTHENTICATION_SALT_KEY'
PERMISSIONS = [
    'public_profile', #includes:id,first_name,last_name,middle_name,name, name_format,picture,short_name
    'email',
]


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
        error = self.request.form.get("error", None)
        errorReason = self.request.form.get("error_reason", None)

        salt = hashlib.sha256().hexdigest()
        sdm = getToolByName(self.context, "session_data_manager")
        session = sdm.getSessionData(create=True)
        session[FB_AUTHENTICATION_SALT_KEY] = salt
        permission_string = ','.join(PERMISSIONS)
        args = {'state': salt,
                'scope': permission_string,
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

        # Check if the status is the same...
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

        response = json.loads(urllib.urlopen(
                "%s?%s" % (FACEBOOK_ACCESS_TOKEN_URL, urllib.urlencode(args),)
            ).read())

        # Load the profile using the access token we just received
        if "access_token" in response:
            accessToken = str(response["access_token"])
        else:
            # AccessToken seems to be wrong
            log.error('Did not get access_token from facebook. Please check that App-Secret-Key is correct!')
            IStatusMessage(self.request).add(_(u"Facebook authentication denied"), type="error")
            self.request.response.redirect(self.context.absolute_url())
            return u""

        fields = 'id,name,short_name,email'
        profile = json.load(urllib.urlopen(
            "%s?fields=%s&%s" % (FACEBOOK_PROFILE_URL, fields, urllib.urlencode({'access_token': accessToken}))
        ))

        userId = profile.get('id').encode("utf-8")
        name = profile.get('name').encode("utf-8")
        email = profile.get('email', '').encode("utf-8")
        username = profile.get('short_name', '').encode("utf-8")

        profile_image = urllib.urlopen(
            "%s?%s" % (FACEBOOK_PROFILE_PICTURE_URL, urllib.urlencode({'access_token': accessToken}),)
        ).read()

        profile_picture_data = urllib.urlopen(
            "%s?type=large&redirect=false&%s" % (FACEBOOK_PROFILE_PICTURE_URL, urllib.urlencode({'access_token': accessToken}))  # noqa :501
        ).read()

        if profile_picture_data:
            profile_image_data = json.loads(profile_picture_data)['data']
            profile_image_url = profile_image_data.get('url', '')

        if not userId or not name:
            IStatusMessage(self.request).add(_(u"Insufficient information in Facebook profile"), type="error")
            self.request.response.redirect(self.context.absolute_url())
            return u""


        # Save the data in the session so that the extraction plugin can
        # authenticate the user to Plone
        session[SessionKeys.accessToken] = accessToken
        session[SessionKeys.userId] = userId
        session[SessionKeys.userName] = username + userId
        session[SessionKeys.fullname] = name
        session[SessionKeys.email] = email
        session[SessionKeys.profile_image] = profile_image
        session[SessionKeys.profile_image_url] = profile_image_url

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
                user_data['portrait'] = session[SessionKeys.profile_image]
                user_data['portrait_url'] = session[SessionKeys.profile_image_url]  # noqa :501
                plugin._storage[session[SessionKeys.userId]] = user_data

        return_args = ''
        if self.request.get('came_from', None) is not None:
            return_args = {'came_from': self.request.get('came_from')}
            return_args = '?' + urllib.urlencode(return_args)

        self.request.response.redirect(self.context.absolute_url() + '/logged_in' + return_args)
