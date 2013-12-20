import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmc,datetime,locale,time,TVStreamer,AdjaranetNavigation,VideoScraper
from datetime import datetime, date, timedelta

nav = AdjaranetNavigation.AdjaranetNavigation()

                        
def CATEGORIES():
        nav.addDir('Sherlock', 'http://adjaranet.com/Movie/main?id=1000080&serie=1', 'TVSeries', '')
        nav.addDir('Elementary', 'http://adjaranet.com/Movie/main?id=1000059&serie=1', 'TVSeries', '')

        
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
       
elif action=='TVSeries':
        print ""+url
	TVStreamer.TVStreamer().AddTvSeasons(url)
	xbmc.executebuiltin("Container.SetViewMode(51)")

elif action=='GetEpisodes':
        print ""+url
        TVStreamer.TVStreamer().GetEpisodes(url, get_params(url))
        xbmc.executebuiltin("Container.SetViewMode(51)")

elif action=='gettvlinks':
        print ""+url
        TVStreamer.TVStreamer().GETTVLINKS(url,name)
        
elif action=='getdaytable':
        TVStreamer.TVStreamer().GETDAYTABLE(url, itemparams)

elif action=='choosetime':
        TVStreamer.TVStreamer().CHOOSETIME(url, itemparams)

elif action=='videos_GetCategories':
        VideoScraper.VideoScraper().GetVideoCategories(url)

elif action=='movie_categories':
        VideoScraper.VideoScraper().GetMovieCategories(url, itemparams)

elif action=='movie_names':
        VideoScraper.VideoScraper().GetMovieNames(url)
	xbmc.executebuiltin("Container.SetViewMode(500)")

elif action=='video_getlinks':
        VideoScraper.VideoScraper().GetVideoLinks(url)
	xbmc.executebuiltin("Container.SetViewMode(500)")

elif action=='movie_links':
        VideoScraper.VideoScraper().GetMovieLinks(url)
	xbmc.executebuiltin("Container.SetViewMode(500)")

elif action=='video_play':
        VideoScraper.VideoScraper().PlayVideo(url, itemparams)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
