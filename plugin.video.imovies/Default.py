import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmc,datetime,locale,time,Navigation,Scraper
from datetime import datetime, date, timedelta

nav = Navigation.Navigation()

                        
def CATEGORIES():
	nav.addDir('Users', '1', 'Users', '')
	nav.addDir('TV Shows', '1', 'TVShowsRoot', '')
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

elif action=='MoviesRoot':
	nav.addDir('Recently Added', 'http://www.imovies.ge/watch', 'ScrapPage', '')
	nav.addDir('Top of IMDB', 'http://www.imovies.ge/watch.php?sort=rating', 'ScrapPage', '')
	nav.addDir('By year', 'http://www.imovies.ge/watch.php?sort=year', 'ScrapPage', '')

elif action=='Users':
	Scraper.Scraper().GetUser('http://www.imovies.ge/users/2091')
	Scraper.Scraper().GetUser('http://www.imovies.ge/users/44657')
	xbmc.executebuiltin("Container.SetViewMode(51)")

elif action=='TVShow':
	print ""+url
	Scraper.Scraper().GetSeasons(url)
	xbmc.executebuiltin("Container.SetViewMode(51)")

elif action=='ScrapPage':
	Scraper.Scraper().GetTvShows(url)
	xbmc.executebuiltin("Container.SetViewMode(500)")

elif action=='GetEpisodes':
	Scraper.Scraper().GetEpisodes(url, itemparams)
	xbmc.executebuiltin("Container.SetViewMode(50)")

xbmcplugin.endOfDirectory(int(sys.argv[1]))
