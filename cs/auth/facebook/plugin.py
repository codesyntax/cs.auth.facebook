import logging

from zope.interface import implements
from zope.publisher.browser import BrowserView

from zope.globalrequest import getRequest

from collective.beaker.interfaces import ISession

from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin

from Products.PluggableAuthService.interfaces.plugins import (
        IExtractionPlugin,
        IAuthenticationPlugin,
        ICredentialsResetPlugin,
        IPropertiesPlugin,
        IRolesPlugin,
        IUserEnumerationPlugin
    )

logger = logging.getLogger('cs.auth.facebook')

class SessionKeys:
    """Constants used to look up session keys
    """
    
    userId      =   "cs.auth.facebook.userId"
    userName    =   "cs.auth.facebook.userName"
    fullname    =   "cs.auth.facebook.fullname"
    accessToken =   "cs.auth.facebook.accessToken"

class AddForm(BrowserView):
    """Add form the PAS plugin
    """
    
    def __call__(self):
        
        if 'form.button.Add' in self.request.form:
            name = self.request.form.get('id')
            title = self.request.form.get('title')
            
            plugin = CSFacebookUsers(name, title)
            self.context.context[name] = plugin
            
            self.request.response.redirect(self.context.absolute_url() +
                    '/manage_workspace?manage_tabs_message=Plugin+added.')

class CSFacebookUsers(BasePlugin):
    """PAS plugin for authentication against facebook.
    
    Here, we implement a number of PAS interfaces, using a session managed
    by Beaker (via collective.beaker) to temporarily store the values we
    have captured.
    """
    
    # List PAS interfaces we implement here
    implements(
            IExtractionPlugin,
            ICredentialsResetPlugin,
            IAuthenticationPlugin,
            IPropertiesPlugin,
            IRolesPlugin,
            IUserEnumerationPlugin,
        )
    
    def __init__(self, id, title=None):
        self.__name__ = self.id = id
        self.title = title
    #
    # IExtractionPlugin
    # 

    
    def extractCredentials(self, request):
        """This method is called on every request to extract credentials.
        In our case, that means looking for the values we store in the
        session.
        
        o Return a mapping of any derived credentials.
        
        o Return an empty mapping to indicate that the plugin found no
          appropriate credentials.
        """
        
        # Get the session from Beaker.
        
        session = ISession(request, None)
        
        if session is None:
            return None
        
        # We have been authenticated and we have a session that has not yet
        # expired:
        
        if SessionKeys.userId in session:
            
            return {
                    'src': self.getId(),
                    'userid': session[SessionKeys.userId],
                    'username': session[SessionKeys.userName],
                }
        
        return None
    
    #
    # IAuthenticationPlugin
    # 
    
    
    def authenticateCredentials(self, credentials):
        """This method is called with the credentials that have been
        extracted by extractCredentials(), to determine whether the user is
        authenticated or not.
        
        We basically trust our session data, so if the session contains a
        user, we treat them as authenticated. Other systems may have more
        stringent needs, but we should avoid an expensive check here, as this
        method may be called very often - at least once per request.
        
        credentials -> (userid, login)
        
        o 'credentials' will be a mapping, as returned by extractCredentials().
        
        o Return a  tuple consisting of user ID (which may be different 
          from the login name) and login
        
        o If the credentials cannot be authenticated, return None.
        """
        
        # If we didn't extract, ignore
        if credentials.get('src', None) != self.getId():
            return
        
        # We have a session, which was identified by extractCredentials above.
        # Trust that it extracted the correct user id and login name
        
        if (
            'userid' in credentials and
            'username' in credentials
        ):
            return (credentials['userid'], credentials['username'],)
        
        return None
    
    #
    # ICredentialsResetPlugin
    # 
    
    def resetCredentials(self, request, response):
        """This method is called if the user logs out.
        
        Here, we simply destroy their session.
        """
        session = ISession(request, None)
        if session is None:
            return
        
        session.delete()
    
    #
    # IPropertiesPlugin
    # 
    
    def getPropertiesForUser(self, user, request=None):
        """This method is called whenever Plone needs to get properties for
        a user. We return a dictionary with properties that map to those
        Plone expect.
        
         user -> {}
        
        o User will implement IPropertiedUser.
        
        o Plugin should return a dictionary or an object providing
          IPropertySheet.
          
        o Plugin may scribble on the user, if needed (but must still
          return a mapping, even if empty).
          
        o May assign properties based on values in the REQUEST object, if
          present
        """
        
        if request is None:
            request = getRequest()
        
        session = ISession(request, None)
        if session is None:
            return {}
        
        # Is this an cs.auth.facebook Facebook user?
        if session.get(SessionKeys.userId, None) != user.getId():
            return {}
        
        return {
                'fullname': session.get(SessionKeys.fullname),
            }
    
    #
    # IRolesPlugin
    # 
    
    def getRolesForPrincipal(self, principal, request=None):
        """Return a list of roles for the given principal (a user or group).
        
        Here, we simply grant the Member role to everyone we have
        authenticated. We could of course have invented a new role as well,
        in which case we'd want to register it in rolemap.xml.
        
        principal -> ( role_1, ... role_N )
        
        o Return a sequence of role names which the principal has.
        
        o May assign roles based on values in the REQUEST object, if present.
        """
        
        if request is None:
            request = getRequest()
        
        session = ISession(request, None)
        if session is None:
            return ()
        
        # Is this an cs.auth.facebook Facebook user?
        if session.get(SessionKeys.userId, None) != principal.getId():
            return ()
        
        return ('Member',)
    
    #
    # IUserEnumerationPlugin
    # 
    
    def enumerateUsers(self 
                      , id=None
                      , login=None
                      , exact_match=False
                      , sort_by=None
                      , max_results=None
                      , **kw
                      ):
        """This function is used to search for users.
        
        We don't implement a search of all of Facebook (!), but it's important
        that we allow Plone to search for the currently logged in user and get
        a result back, so we effectively implement a search against only one
        value.
        
         -> ( user_info_1, ... user_info_N )
        
        o Return mappings for users matching the given criteria.
        
        o 'id' or 'login', in combination with 'exact_match' true, will
          return at most one mapping per supplied ID ('id' and 'login'
          may be sequences).
          
        o If 'exact_match' is False, then 'id' and / or login may be
          treated by the plugin as "contains" searches (more complicated
          searches may be supported by some plugins using other keyword
          arguments).
          
        o If 'sort_by' is passed, the results will be sorted accordingly.
          known valid values are 'id' and 'login' (some plugins may support
          others).
          
        o If 'max_results' is specified, it must be a positive integer,
          limiting the number of returned mappings.  If unspecified, the
          plugin should return mappings for all users satisfying the criteria.
          
        o Minimal keys in the returned mappings:
        
          'id' -- (required) the user ID, which may be different than
                  the login name
                  
          'login' -- (required) the login name
          
          'pluginid' -- (required) the plugin ID (as returned by getId())
          
          'editurl' -- (optional) the URL to a page for updating the
                       mapping's user
                       
        o Plugin *must* ignore unknown criteria.
        
        o Plugin may raise ValueError for invalid criteria.
        
        o Insufficiently-specified criteria may have catastrophic
          scaling issues for some implementations.
        """
        
        request = getRequest()
        session = ISession(request, None)
        if session is None:
            return ()
        
        if exact_match and id == session.get(SessionKeys.userId, None):
            return ({
                'id': session[SessionKeys.userId],
                'login': session[SessionKeys.userName],
                'pluginid': self.getId(),
            },)
        
        return ()
