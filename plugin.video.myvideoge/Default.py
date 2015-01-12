import urllib,urllib2,re,datetime,locale,time,Scraper, os
import xbmcplugin, xbmcgui, xbmc, xbmcaddon
from datetime import datetime, date, timedelta
from Lib.Navigation import Navigation

addon = xbmcaddon.Addon()
addonID = addon.getAddonInfo('id')
nav = Navigation()

usersFilePath = xbmc.translatePath("special://profile/addon_data/" + addonID + "/users.json")

while (not os.path.exists(xbmc.translatePath("special://profile/addon_data/"+addonID+"/settings.xml"))):
	addon.openSettings()

def get_params(paramstring = sys.argv[2]):
        param = []
        if len(paramstring) >= 2:
                params = paramstring
                cleanedparams = params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param




              
params = get_params()
url = None
name = None
action = None
itemparams = None

try:
        url = urllib.unquote_plus(params["url"])
except:
        pass
try:
        name = urllib.unquote_plus(params["name"])
except:
        pass
try:
        action = params["action"]
except:
        pass
try:
        itemparams = urllib.unquote_plus(params["params"])
        if itemparams != None and len(itemparams):
                itemparams = get_params(itemparams)
except:
        pass


print "Mode: " + str(action)
print "URL: " + str(url)
print "Name: " + str(name)


if action==None or url==None or len(url)<1:
	nav.addDir('TV', 'http://www.myvideo.ge/c/livetv', 'Channels', '')
	nav.addDir('Video Channels', '#', 'VideoChannels', '')
	xbmc.executebuiltin("Container.SetViewMode(50)")
       
elif action=='Channels':
	Scraper.Scraper().GetChannels(url)
	xbmc.executebuiltin("Container.SetViewMode(500)")

elif action=='GetTvSchedule':
	Scraper.Scraper().GetTvSchedule(url, itemparams)
	xbmc.executebuiltin("Container.SetViewMode(50)")
	
elif action=='JumpOnTime':
	Scraper.Scraper().JumpOnTime(url, itemparams)
	
elif action=='PlayByTime':
	Scraper.Scraper().PlayByTime(url, itemparams)
	
elif action=='PlayTV':
	Scraper.Scraper().PlayTV(url, itemparams)
		
elif action=='PlayLiveTV':
	Scraper.Scraper().PlayLiveTV(url)

elif action=='GetVideos':
	Scraper.Scraper().GetVideos(url, itemparams)
	xbmc.executebuiltin("Container.SetViewMode(500)")
	
elif action=='VideoChannels':
	Scraper.Scraper().LoadVideoChannels()
	nav.addDir('Add Channel', '#', 'AddVideoChannel', 'http://icons.iconarchive.com/icons/fatcow/farm-fresh/32/television-add-icon.png', isFolder=False)
	nav.addDir('Add User', '#', 'AddUser', 'http://icons.iconarchive.com/icons/fasticon/fast-icon-users/48/add-user-icon.png', isFolder=False)
	xbmc.executebuiltin("Container.SetViewMode(500)")
	
elif action=='AddVideoChannel':
	Scraper.Scraper().AddVideoChannel()
	xbmc.executebuiltin("Container.Refresh")
	
elif action=='AddUser':
	Scraper.Scraper().AddUser()
	xbmc.executebuiltin("Container.Refresh")	

elif action=='RemoveVideoChannels':
	Scraper.Scraper().RemoveVideoChannels(url)
	xbmc.executebuiltin("Container.Refresh")	

elif action=='PlayVideo':
	Scraper.Scraper().PlayVideo(url, name)
		
xbmcplugin.endOfDirectory(int(sys.argv[1]))
