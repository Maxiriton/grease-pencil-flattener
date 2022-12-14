import bpy

def get_addon_prefs():
    '''
    function to read current addon preferences properties

    access a prop like this :
    prefs = get_addon_prefs()
    option_state = prefs.super_special_option

    oneliner : get_addon_prefs().super_special_option
    '''
    import os
    addon_name = os.path.splitext(__name__)[0]
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[addon_name].preferences
    return (addon_prefs)