import urllib,urllib2,re,datetime,locale,time
import Navigation, Scraper, Dialogs
from datetime import datetime, date, timedelta
import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import os

nav = Navigation.Navigation()
addon = xbmcaddon.Addon()
addonID = addon.getAddonInfo('id')
                        
while (not os.path.exists(xbmc.translatePath("special://profile/addon_data/"+addonID+"/settings.xml"))):
	addon.openSettings()						
						
def CATEGORIES():
	nav.addDir('TV Shows', 'http://adjaranet.com/Search/SearchResults?ajax=1&display=120&offset=0&orderBy=date&order%5Border%5D=desc&order%5Bdata%5D=published&country=false&episode=1', 'TVShows', '')
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
       
elif action=='TVShows':
	Scraper.Scraper().AddTvShows(url)
	xbmc.executebuiltin("Container.SetViewMode(500)")

elif action=='TVShow':
	Scraper.Scraper().AddTvSeasons(url, itemparams)
	xbmc.executebuiltin("Container.SetViewMode(51)")

elif action=='GetEpisodes':
        Scraper.Scraper().GetEpisodes(url, get_params(url), itemparams)
        xbmc.executebuiltin("Container.SetViewMode(51)")
		
elif action=='ChooseLanguage':
        languages = Scraper.Scraper().GetLanguages(params["id"])
	if len(languages) > 0:
		ret = xbmcgui.Dialog().select("Choose Language", languages)
		url = url.format(languages[ret])
		xbmc.Player().play(url)
	else:
		xbmcgui.Dialog().ok("Warning", "No languages found")
	
elif action=='MoviesRoot': 
	nav.addDir('Collectons', 'http://adjaranet.com/Collections/', 'MovieCollections', '')
	Scraper.Scraper().LoadMovies()
	nav.addDir('Add Movie', '1', 'AddMovie', 'http://icons.iconarchive.com/icons/dryicons/aesthetica-2/128/movie-track-add-icon.png', isFolder=False)
	xbmc.executebuiltin("Container.SetViewMode(51)")
	
elif action=='AddMovie':
	Scraper.Scraper().AddMovie()
	xbmc.executebuiltin("Container.Refresh")

elif action=='RemoveMovie':
	Scraper.Scraper().RemoveMovie(url)
	xbmc.executebuiltin("Container.Refresh")
	
elif action=='MovieCollections':
	Scraper.Scraper().GetCollections(url)
	xbmc.executebuiltin("Container.SetViewMode(51)")
	
elif action=='GetMovies':
	Scraper.Scraper().GetMovies(url);
	xbmc.executebuiltin("Container.SetViewMode(500)")
	
elif action=='PlayMovie':
	Scraper.Scraper().PlayMovie(url)
	
elif action=='PlayMovieAs':
	Scraper.Scraper().PlayMovieAs(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))