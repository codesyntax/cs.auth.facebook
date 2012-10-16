from zope.interface import implements
from interfaces import IFacebookUser
from Products.PlonePAS.plugins.ufactory import PloneUser

class FacebookUser(PloneUser):
    implements(IFacebookUser)

