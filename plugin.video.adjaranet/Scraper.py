import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmc,datetime,locale,time,Navigation,string,json,sys
from datetime import datetime, date, timedelta
from Lib.net import Net
import CommonFunctions

nav = Navigation.Navigation()
net = Net()
common = CommonFunctions
common.plugin = "plugin.video.imovies"
common.dbg = True
common.dbglevel = 2

class Scraper:
    
	def AddTvShows(self, url):
		content = net.http_GET(url).content
		data = json.loads(content)
		
		for row in data["data"]:
			nav.addDir(row["title_en"], row["link"], 'TVShow', row["poster"], {"title": row["title_en"].encode('utf8')})
	
	def AddTvSeasons(self, url, params):
		urlMatcher = re.compile('http://adjaranet.com/Movie/main\\?id=([0-9]+)&serie=([0-9]+)', re.DOTALL).findall(url)
		movieId = urlMatcher[0][0]
		season = 1
		while season > 0:
			seasonsUrl = 'http://adjaranet.com/req/series/req.php?reqId=series_list&id=' + movieId + '&season=' + str(season)
			
			req = urllib2.Request(seasonsUrl)
			req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
			u = urllib2.urlopen(req)
			result = json.load(u)
			u.close()
			      
			if len(result) > 0:
				title = 'Season ' + str(season)
				nav.addDir(title, seasonsUrl, 'GetEpisodes', 'http://static.adjaranet.com/moviecontent/' + str(movieId) + '/covers/214x321-' + str(movieId) + '.jpg', {"title": params["title"]})
				season = season + 1
			else:
				season = 0
	
	def GetEpisodes(self, url, url_params, params):
		req = urllib2.Request(url)
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
		u = urllib2.urlopen(req)
		result = json.load(u)
		u.close()
			
		for row in result:
			url = 'rtmp://edge2.vod.adjaranet.com/vod playpath=mp4:{0}/{0}_{1}_{2}_{3}_800'.format(url_params['id'], url_params['season'].rjust(2, '0'), row['episode'].rjust(2, '0'), 'English')
			li = xbmcgui.ListItem(row['name'], iconImage = '', thumbnailImage = '')
			li.setInfo( type= "Video", 
                                infoLabels =
                                        {
                                             "title": row['name'],
                                             "episode": row['episode'],
                                             "season": url_params["season"],
                                             "tvshowtitle": params["title"]
                                        } )
			url_without_language = 'rtmp://edge2.vod.adjaranet.com/vod playpath=mp4:{0}/{0}_{1}_{2}_{3}_800'.format(url_params['id'], url_params['season'].rjust(2, '0'), row['episode'].rjust(2, '0'), '{0}')
                        li.addContextMenuItems([('Choose Language', 'XBMC.RunPlugin(%s?action=ChooseLanguage&id=%s&url=%s)' % (sys.argv[0], row['id'], urllib.quote_plus(url_without_language)))]) 
			xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = url, listitem = li)

	def GetLanguages(self, id):
		req_url = "http://adjaranet.com/req/series/req.php?id={0}&reqId=info".format(id)
		content = net.http_GET(req_url).content
		
		ge = common.parseDOM(content, "video", ret = "ge")
		ru = common.parseDOM(content, "video", ret = "ru")
		en = common.parseDOM(content, "video", ret = "en")
		
		languages = []
		if (common.makeAscii(ge) == "1"):
			languages.append("Georgian")
		if (common.makeAscii(ru) == "1"):
			languages.append("Russian")
		if (common.makeAscii(en) == "1"):
			languages.append("English")
			
		return languages
		
