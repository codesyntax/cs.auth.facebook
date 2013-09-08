Introduction
============

A PAS plugin to login into a Plone Site using Facebook.


Installation and getting started
-----------------------------------

Add 'cs.auth.facebook' to your buildout.cfg's eggs list.

You have to add a configuration similar to this to your buildout.cfg's `instance` section::

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

Install the product in the Plone Control Panel

Create a new Facebook app at https://developers.facebook.com/app and fill in the
required data in the plugin's control panel form.


Credit
--------

This product re-distributes a lot of code written by Martin Aspeli
(aka @optilude) in his book "Professional Plone 4 Development" and
available under GPL license in his personal GitHub account with
the name 'optilux.facebookauth':

  https://github.com/optilude/optilux/tree/chapter-16/src/optilux.facebookauth

