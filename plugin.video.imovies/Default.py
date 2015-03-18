import urllib,urllib2,re
import xbmc,xbmcplugin,xbmcgui,xbmcaddon
import datetime,locale,time,Navigation,Scraper
import os
from datetime import datetime, date, timedelta

addon = xbmcaddon.Addon()
addonID = addon.getAddonInfo('id')
nav = Navigation.Navigation()

usersFilePath = xbmc.translatePath("special://profile/addon_data/" + addonID + "/users.json")

while (not os.path.exists(xbmc.translatePath("special://profile/addon_data/"+addonID+"/settings.xml"))):
	addon.openSettings()

                        
def CATEGORIES():
	nav.addDir('Users', '1', 'Users', '')
	nav.addDir('Lists', '1', 'Lists', '')
	nav.addDir('TV Shows', '1', 'TVShowsRoot', '')
	nav.addDir('Channels', '1', 'ChannelsRoot', '')
	nav.addDir('Movies', '1', 'MoviesRoot', '')

        
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
        print ""
        CATEGORIES()
       
elif action=='TVShowsRoot':
	nav.addDir('Recently Added', 'http://www.imovies.ge/tvseries', 'ScrapPage', '')
	Scraper.Scraper().LoadTvShows()
	nav.addDir('Add TV Show', 'http://www.imovies.ge/movies/', 'AddTvShow', 'http://icons.iconarchive.com/icons/dryicons/aesthetica-2/128/movie-track-add-icon.png', isFolder=False)

elif action=='ChannelsRoot':
	Scraper.Scraper().LoadChannels()
	nav.addDir('Add Channel', '#', 'AddChannel', 'http://icons.iconarchive.com/icons/dryicons/aesthetica-2/128/movie-track-add-icon.png', isFolder=False)

elif action=='MoviesRoot':
	nav.addDir('Recently Added', 'http://www.imovies.ge/watch', 'ScrapPage', '')
	nav.addDir('Top of IMDB', 'http://www.imovies.ge/watch.php?sort=rating', 'ScrapPage', '')
	nav.addDir('By year', 'http://www.imovies.ge/watch.php?sort=year', 'ScrapPage', '')

elif action=='Users':
	Scraper.Scraper().LoadUsers()
	nav.addDir('Add User', 'http://www.imovies.ge/users/', 'AddUser', 'http://icons.iconarchive.com/icons/fasticon/fast-icon-users/48/add-user-icon.png', isFolder=False)
	xbmc.executebuiltin("Container.SetViewMode(51)")

elif action=='Lists':
	Scraper.Scraper().LoadLists()
	nav.addDir('Add List', 'http://www.imovies.ge/lists/', 'AddList', 'http://icons.iconarchive.com/icons/visualpharm/icons8-metro-style/48/Adds-Add-list-icon.png', isFolder=False)
	xbmc.executebuiltin("Container.SetViewMode(51)")

elif action=='TVShow':
	print ""+url
	Scraper.Scraper().GetSeasons(url)
	xbmc.executebuiltin("Container.SetViewMode(51)")

elif action=='ScrapPage':
	Scraper.Scraper().GetTvShows(url)
	xbmc.executebuiltin("Container.SetViewMode(500)")

elif action=='ScrapListPage':
	Scraper.Scraper().ScrapListPage(url)
	xbmc.executebuiltin("Container.SetViewMode(500)")

elif action=='GetEpisodes':
	Scraper.Scraper().GetEpisodes(url, itemparams)
	xbmc.executebuiltin("Container.SetViewMode(50)")

elif action=='AddUser':
	Scraper.Scraper().AddUser()
	xbmc.executebuiltin("Container.Refresh")

elif action=='RemoveUser':
	Scraper.Scraper().RemoveUser(url)
	xbmc.executebuiltin("Container.Refresh")

elif action=='AddList':
	Scraper.Scraper().AddList()
	xbmc.executebuiltin("Container.Refresh")

elif action=='RemoveList':
	Scraper.Scraper().RemoveList(url)
	xbmc.executebuiltin("Container.Refresh")

elif action=='AddTvShow':
	Scraper.Scraper().AddTvShow()
	xbmc.executebuiltin("Container.Refresh")

elif action=='RemoveTvShow':
	Scraper.Scraper().RemoveTvShow(url)
	xbmc.executebuiltin("Container.Refresh")

elif action=='AddChannel':
	Scraper.Scraper().AddChannel()
	xbmc.executebuiltin("Container.Refresh")

elif action=='RemoveChannel':
	Scraper.Scraper().RemoveChannel(url)
	xbmc.executebuiltin("Container.Refresh")

elif action=='Channel':
	Scraper.Scraper().ScrapChannelPage(url)
	
elif action=='ScrapVideoPage':
	Scraper.Scraper().ScrapVideoPage(url)
	
elif action=="PlayVideo":
	Scraper.Scraper().PlayVideo(url)
	
xbmcplugin.endOfDirectory(int(sys.argv[1]))
