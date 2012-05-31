from StringIO import StringIO

from Products.PlonePAS.Extensions.Install import activatePluginInterfaces

from cs.auth.facebook.plugin import CSFacebookUsers

def installPASPlugin(portal, name='cs-facebook-users'):
    
    out = StringIO()
    userFolder = portal['acl_users']
    
    if name not in userFolder:
        
        plugin = CSFacebookUsers(name, 'CS Facebook Users')
        userFolder[name] = plugin
        
        # Activate all interfaces
        activatePluginInterfaces(portal, name, out)
        
        # Move plugin to the top of the list for each active interface
        plugins = userFolder['plugins']
        for info in plugins.listPluginTypeInfo():
            interface = info['interface']
            if plugin.testImplements(interface):
                active = list(plugins.listPluginIds(interface))
                if name in active:
                    active.remove(name)
                    active.insert(0, name)
                    plugins._plugins[interface] = tuple(active)
        
        return out.getvalue()

def importVarious(context):
    """Miscellanous steps import handle
    """
    
    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a 
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.
    
    if context.readDataFile('cs.auth.facebook-various.txt') is None:
        return
    
    portal = context.getSite()
    
    installPASPlugin(portal)
