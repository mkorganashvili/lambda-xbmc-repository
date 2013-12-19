import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmc,datetime,locale,time,MyVideoNavigation
from datetime import datetime, date, timedelta

nav = MyVideoNavigation.MyVideoNavigation()
    
class VideoScraper:
    
    def GetVideoCategories(self, url):
        nav.addDir('ყველა', 'http://www.myvideo.ge/?act=main', 'video_getlinks', '')
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        match = re.compile('<li><a href="index.php\?cat_id=(.+?)" style="">(.+?)</a> <span class="video_count">(.+?)</span></li>').findall(link)
        for cat_id, name, count in match:
                nav.addDir('%s (%s)' % (name, count), 'http://www.myvideo.ge/index.php?cat_id=' + cat_id, 'video_getlinks', '')
                
    def GetMovieCategories(self, url, params = {}):
        nav.addDir('ყველა', url, 'movie_names', '')
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        if url.find('movie_par_id') == -1:
            match = re.compile('href="\?act=movie&movie_par_id=(.+?)">(.+?)</a></div>').findall(link)
            for par_id, name in match:
                    nav.addDir('%s' % (name), 'http://www.myvideo.ge/?act=movie&movie_par_id=' + par_id, 'movie_categories', '', params = { 'par_id': par_id })
        else:
            match = re.compile('act=movie&movie_par_id=%s&movie_cat_id=(.+?)">(.+?)</a>' % params['par_id']).findall(link)
            for cat_id, name in match:
                    nav.addDir('%s' % (name), 'http://www.myvideo.ge/?act=movie&movie_par_id=%s&movie_cat_id=%s' % (params['par_id'], cat_id) , 'movie_names', '')
            
                    
    def GetVideoLinks(self, url):
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
            response = urllib2.urlopen(req)
            link=response.read()
            response.close()
            videoTags = re.compile('<div class="vid">(.+?)<div class="vid_desc">(.+?)</div>', re.DOTALL).findall(link)
            print 'len: ' + str(len(videoTags))
            for tag1, tag2 in videoTags:
                video_id = re.compile('<a href="/\?video_id=(.+?)"').findall(tag1)[0]
                thumbnail = re.compile('<img src="(.+?)"').findall(tag1)[0]
                name = re.compile('title="(.+?)" >').findall(tag2)[0]
                print 'img: ' + thumbnail
                params = { "video_id": video_id, "thumbnail": thumbnail }
                nav.addDir(name, 'http://www.myvideo.ge/?video_id=' + video_id, 'video_play', thumbnail, thumbnail = thumbnail.replace('.ge', '.ge/screens'), isFolder=False, params = params) 
   
    def GetMovieNames(self, url):
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
            response = urllib2.urlopen(req)
            link=response.read()
            response.close()
            videoTags = re.compile('<div class="vid"(.+?)</div>(.+?)</div>', re.DOTALL).findall(link)
            print 'len: ' + str(len(videoTags))
            for tag1, tag2 in videoTags:
                movie_id = re.compile('act=movie&movie_id=(.+?)"').findall(tag1)[0]
                thumbnail = re.compile('<img(.+?)src="(.+?)"').findall(tag1)[0][1]
                name = re.compile('title="(.+?)"').findall(tag2)[0]
                print 'img: ' + thumbnail
                params = { "movie_id": movie_id, "thumbnail": thumbnail }
                nav.addDir(name, 'http://www.myvideo.ge/?act=movie&movie_id=' + movie_id, 'movie_links', thumbnail, params = params) 
   
    def GetMovieLinks(self, url):
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
            response = urllib2.urlopen(req)
            link=response.read()
            response.close()
            videoTags = re.compile('<tr id="(.+?)</tr>', re.DOTALL).findall(link)
            print 'len: ' + str(len(videoTags))
            for tag1 in videoTags:
                video_id = re.compile('video_id=(.+?)"').findall(tag1)[0]
                thumbnail = re.compile('<img(.+?)src="(.+?)"').findall(tag1)[0][1]
                name = re.compile('<a class="ses_title"(.+?)>(.+?)</a>').findall(tag1)[0][1]
                print 'img: ' + thumbnail
                params = { "video_id": video_id, "thumbnail": thumbnail }
                nav.addDir(name, 'http://www.myvideo.ge/?video_id=' + video_id, 'video_play', thumbnail, params = params, isFolder=False) 
   
    def PlayVideo(self, url, params):
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
            response = urllib2.urlopen(req)
            link=response.read()
            response.close()
    
            dvr = ''
            match = re.compile("{url: '(.+?)'").findall(link)                      
            
            if (not len(match)):
                if (link.find('log_in.php') == -1):
                    xbmcgui.Dialog().ok('შეცდომა', 'სამწუხაროდ ფაილი არ მოიძებნა')
                    return
                else:
                    yn = xbmcgui.Dialog().yesno('შეცდომა', 'ფაილის ნახვა შეზღუდულია!', 'ვცადოთ ინექცია?', '', 'არა', 'კი')
                    if not yn:
                        return
                    else:
                        thumbId = re.compile("ge(.+?)\.").findall(params['thumbnail'])
                        print 'truhu: ' + str(thumbId) + ' '+ params['thumbnail']
                        if not len(thumbId):
                            xbmcgui.Dialog().ok('შეცდომა', 'სამწუხაროდ ინფორმაცია მიუწვდომელია')
                            return
                            
                        dvr = 'http://silk1.vod.myvideo.ge/flv' + thumbId[0] + '.flv'
                        try:
                            f = urllib2.urlopen(urllib2.Request(dvr))
                            f.close()
                        except:
                            dvr = 'http://silk1.vod.myvideo.ge/flv' + thumbId[0] + '.mp4'
                            #f.close()
            
            for m in match:
                print 'm: ' + str(m.find(params['video_id']))
                if m.find(params['video_id']) > -1 and m.find('jpg') == -1:
                    dvr = m
                
            playUrl = dvr

            netConnectionUrl = re.compile("netConnectionUrl: '(.+?)'").findall(link)                    
            if len(netConnectionUrl):
                connectionArgs = re.compile("connectionArgs: \[ '(.+?)'").findall(link)[0]
                app = re.compile("ge/(.+?)").findall(netConnectionUrl[0])[0]
                playUrl = '%s playPath=%s app=%s swfUrl=http://embed.myvideo.ge/flv_player/flowplayer.rtmp-3.1.3.swf pageURL=http://www.myvideo.ge/?video_id=1250099 conn=S:%s' % (netConnectionUrl[0], dvr, app, connectionArgs)
 
            player = xbmc.Player()
            player.play(playUrl)
            print 'dvr: ' + dvr
