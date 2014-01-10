import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmc,datetime,locale,time,Scraper
from datetime import datetime, date, timedelta
from Lib.Navigation import Navigation

nav = Navigation()

        
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
        nav.addDir('Channels', 'http://www.iptv.ge/en/tv/', 'Channels', '')
        xbmc.executebuiltin("Container.SetViewMode(51)")
       
elif action=='Channels':
		Scraper.Scraper().GetChannels(url)
		xbmc.executebuiltin("Container.SetViewMode(500)")

elif action=='MyVideo':
        nav.addLink('Rustavi 2 HQ', 'rtmp://edge4-5.co.myvideo.ge/dvrh264/rustavi2hq app=dvrh264/rustavi2hq playpath=rustavi2hq swfUrl=http://www.myvideo.ge/dvr/dvrGoogle21.swf?v=1.8b pageURL=http://www.myvideo.ge live=true', '')
        nav.addLink('', '', '')
        nav.addLink('', '', '')
        xbmc.executebuiltin("Container.SetViewMode(50)")

		
xbmcplugin.endOfDirectory(int(sys.argv[1]))
