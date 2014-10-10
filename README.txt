Introduction
============

A PAS plugin to login into a Plone Site using Facebook.

* Log in to a Plone site through Facebook: when a user requests to log in to the Plone site he will be redirected to Facebook so that he provides the credentials there, then he will be redirected back to the Plone site and will be identified there.

* The user will be a standard Plone user, so Roles or Group membership can be set.

* Minimal user information is kept in Plone such as full name, Facebook ID, photo and e-mail (if available) of the user. This is kept to avoid permanent requests to Facebook API. This information is refreshed each time the user logs in to the site.


Installation and getting started
-----------------------------------

Add `cs.auth.twitter` to your buildout.cfg's eggs list. It will install all required dependencies.

You have to add a configuration similar to this to the `[instance]`
section of your buildout file::


 zope-conf-additional =
    <product-config beaker>
        session type     file
        session.data_dir ${buildout:directory}/var/sessions/data
        session.lock_dir ${buildout:directory}/var/sessions/lock
        session.key      beaker.session
        session.secret   this-is-my-secret-${buildout:directory}
    </product-config>

This is needed because we are using collective.beaker to handle Facebook login
session information.

Install the product in the Plone Control Panel. This will create a "Login with
Twitter" action into the personal tools toolbar in Plone.

Create a new Facebook app at https://developers.facebook.com/app and fill in the
required data in the plugin's control panel form.


Credit
--------

This product re-distributes a lot of code written by Martin Aspeli
(aka @optilude) in his book "Professional Plone 4 Development" and
available under GPL license in his personal GitHub account with
the name 'optilux.facebookauth':

  https://github.com/optilude/optilux/tree/chapter-16/src/optilux.facebookauth


Compatibility
==============

Plone 4.x
