from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.interface import Interface

class IFacebookLoginLayer(IDefaultBrowserLayer):
    """
    Zope 3 browser layer for collective.facebooklogin.
    """


class IFacebookUser(Interface):
    """
    Marker interface for Users logged in through Twitter

    """

class ICSFacebookPlugin(Interface):
    """
    Marker interface
    """
    

class IFBLUtils(Interface):
    """
    Marker for utility view
    """
    
    def enabled_on_login_form(self):
        """ check if enabled """
        pass
    
    def fb_app_id(self):
        """ return app_id for JavaScript SDK """
        pass
    