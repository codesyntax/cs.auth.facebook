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
