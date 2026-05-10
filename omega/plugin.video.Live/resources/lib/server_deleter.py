import xbmc, xbmcgui, xbmcaddon, os

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
# সার্ভার ফোল্ডার পাথ
server_dir = xbmc.translatePath(os.path.join('special://home/addons/', addon_id, 'resources/lib/servers/'))

def delete_server():
    # ফোল্ডারের সব সার্ভার ফাইলের লিস্ট নেওয়া
    files = [f for f in os.listdir(server_dir) if f.endswith('.py') and f != '__init__.py']
    
    if not files:
        xbmcgui.Dialog().notification('Delete', 'No custom servers found!', xbmcgui.NOTIFICATION_INFO, 3000)
        return

    # ইউজারকে ফাইল সিলেক্ট করতে বলা
    selected = xbmcgui.Dialog().select('Select Server to Delete', files)
    
    if selected != -1:
        file_to_delete = os.path.join(server_dir, files[selected])
        confirm = xbmcgui.Dialog().yesno('Confirm Delete', f'Are you sure you want to delete {files[selected]}?')
        
        if confirm:
            os.remove(file_to_delete)
            xbmcgui.Dialog().notification('Success', 'Server Deleted Successfully', xbmcgui.NOTIFICATION_INFO, 3000)
            # কোডি রিফ্রেশ করা যাতে মেনু থেকে চলে যায়
            xbmc.executebuiltin('Container.Refresh')

if __name__ == '__main__':
    delete_server()