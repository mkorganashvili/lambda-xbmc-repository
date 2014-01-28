import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmc,datetime,locale,time,Navigation,Scraper
from datetime import datetime, date, timedelta

nav = Navigation.Navigation()

                        
def CATEGORIES():
        nav.addDir('Users', '1', 'Users', '')
        nav.addDir('TV Shows', '1', 'TVSeriesRoot', '')

        
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
       
elif action=='TVSeriesRoot':
        nav.addDir('Elementary', 'http://www.imovies.ge/movies/37815', 'TVSeries', '')
        nav.addDir('Klondike', 'http://www.imovies.ge/movies/42824', 'TVSeries', '')

elif action=='Users':
        Scraper.Scraper().GetUser('http://www.imovies.ge/users/2091')
        Scraper.Scraper().GetUser('http://www.imovies.ge/users/44657')
        xbmc.executebuiltin("Container.SetViewMode(51)")

elif action=='TVSeries':
        print ""+url
	Scraper.Scraper().GetSeasons(url)
	xbmc.executebuiltin("Container.SetViewMode(51)")

elif action=='WatchList':
        Scraper.Scraper().GetWatchlist(url)
        xbmc.executebuiltin("Container.SetViewMode(500)")

elif action=='GetEpisodes':
        print ""+url
        Scraper.Scraper().GetEpisodes(url, itemparams)
        xbmc.executebuiltin("Container.SetViewMode(50)")

xbmcplugin.endOfDirectory(int(sys.argv[1]))
