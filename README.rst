Introduction
============

A PAS plugin to login into a Plone Site using Facebook.

* Log in to a Plone site through Facebook: when a user requests to log in to the Plone site he will be redirected to Facebook so that he provides the credentials there, then he will be redirected back to the Plone site and will be identified there.

* The user will be a standard Plone user, so Roles or Group membership can be set.

* Minimal user information is kept in Plone such as full name, Facebook ID, photo and e-mail (if available) of the user. This is kept to avoid permanent requests to Facebook API. This information is refreshed each time the user logs in to the site.


Installation and getting started
--------------------------------

1. Buildout

   Add `cs.auth.facebook` to your ``buildout.cfg`` eggs list::

    [buildout]
    ...
    eggs =
        cs.auth.facebook
        
   Or as an required install dependency of your own addon ``setup.py``::

    install_requires=[
        ...
        'cs.auth.facebook',
    ], 

2. Create a new Facebook app at https://developers.facebook.com/app and fill 
   in the required data in the plugin's control panel form.

3. Install the product in the Plone Control Panel and provide the app_id 
   and app_secret in the configuration panel.

   Now you see the "Facebook Login" button viewlet. To customize the placement of this
   viewlet please check out the `Plone Viewlet Documentation <http://goo.gl/RyUORn>`_ 

4. Alternatively you can enable an action in portal_actions with the following configuration
   (see ``profiles/default/actions.xml`` within this package)::

    <object name="portal_actions" meta_type="Plone Actions Tool"
       xmlns:i18n="http://xml.zope.org/namespaces/i18n">
        <object name="user" meta_type="CMF Action Category">
            <object name="login_facebook" meta_type="CMF Action" i18n:domain="cs.auth.facebook">
                <property name="title" i18n:translate="">Log in with Facebook</property>
                <property name="description" i18n:translate=""></property>
                <property name="url_expr">string:${globals_view/navigationRootUrl}/@@facebook-login</property>
                <property name="icon_expr"></property>
                <property name="available_expr">python:member is None</property>
                <property name="permissions">
                    <element value="View"/>
                </property>
                <property name="visible">False</property>
            </object>
        </object>
    </object>


Behind the scenes
-----------------

The Facebook Login Viewlet uses the new Facebook JavaScript SDK v2.1 to ensure
the proper popup for every target device. You don't have to care about this.

For more information on FB JSDK checkout the `Facebook Developers Login Documentation <https://developers.facebook.com/docs/facebook-login/login-flow-for-web/v2.1>`_


Credit
------

This product re-distributes a lot of code written by Martin Aspeli
(aka @optilude) in his book "Professional Plone 4 Development" and
available under GPL license in his personal GitHub account with
the name 'optilux.facebookauth':

  https://github.com/optilude/optilux/tree/chapter-16/src/optilux.facebookauth


Compatibility
=============

Plone 4.x
