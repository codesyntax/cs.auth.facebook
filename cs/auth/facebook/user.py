from zope.interface import implements
from interfaces import IFacebookUser
from Products.PluggableAuthService.PropertiedUser import PropertiedUser

class FacebookUser(PropertiedUser):
    implements(IFacebookUser)

