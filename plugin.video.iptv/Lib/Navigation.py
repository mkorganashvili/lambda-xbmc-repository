import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmc,sys

class Navigation:
    def addLink(self, name, url, iconimage, thumbnail = ''):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=thumbnail)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok


    def addDir(self, name, url, action, iconimage, params = {}, isFolder=True, thumbnail = ''):
        u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&action=" + action + "&name=" + urllib.quote_plus(name)
        if (len(params)):
                str_params = ''
                for key in params:
                        str_params += '&%s=%s' % (key, params[key])
                u += '&params=' + urllib.quote_plus(str_params)
        ok = True
        liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=thumbnail)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder)
        return ok
            
