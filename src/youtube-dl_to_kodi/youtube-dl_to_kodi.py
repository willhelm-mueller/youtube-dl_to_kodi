#!/data/data/com.termux/files/usr/bin/python
# Send media links to Kodi  
# if no deep link is provided 
# youtube-dl lib may help to extract those
#
#
#
#

import json
import sys
import argparse
import requests
import youtube_dl
import urllib


###
# initializing basic logging 
### 

import logging

logging.basicConfig(format  = '%(asctime)s %(message)s', 
                    datefmt = '%Y-%m-%d %H:%M:%S',
                    level   = logging.INFO
                    )

logger = logging.getLogger()

###
# dealing with cmd arguments
###

parser = argparse.ArgumentParser(
  description='Submission script from cmd to kodi, if no direct media\
 is given youtube-dl lib is used to extract deeplinks')
parser.add_argument("-u","--url",help="Video url")
parser.add_argument("--host",'-i',    default="raspberry",help="Host default is raspberry")
parser.add_argument("-p","--port",    default='80',help="Port default is 8181(PlayIt) or 80 classic")
parser.add_argument("--max_width", type=int,  default=10000,help="Set maximumg width for playback, youtubt_dl only")
parser.add_argument("-d","--debug",   default=False, action='store_true' ,help="enable debug output")


args = parser.parse_args()

if args.debug:
  logger.level=logging.DEBUG

logger.debug('start logging')




def run_youtube_dl (url):
  """if no direct media was given lets try to resolve deep links via youtube_dl 
  must be available as library !!
  
  url : the input url
  
  returns the deep link via youtube-dl extraction 
  """

  ydl_opts = {
    'logger': logger,
  }
  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    meta = ydl.extract_info(url , download=False) 
    max_width = 0
    ###
    # collect available formats
    ###
    
    if 'formats' not in meta and 'url' in meta: 
      logger.debug(meta)
      return meta['url']
    
    for entry in meta['formats']:
      
      ###
      # skipp those nasty video or audio only streams
      ###
      if 'acodec' in entry and 'vcodec' in entry:
        if entry['vcodec'] == 'none' or entry['acodec'] == 'DASH audio' or entry['acodec'] == 'none':
          continue
      if 'width' in entry and int(entry['width'])  > max_width and int(entry['width']) < args.max_width:
        max_width = int( entry['width'] )
        
      if 'acodec' in entry and 'vcodec' in entry:
        logger.debug('Audio {} Video {} format {} note {} width {}'.format (entry['acodec'],entry['vcodec'],entry['format'], entry['format_note'],entry['width']) )
  
    ###
    # getting 'best' format 
    ###
  
    for entry in meta['formats']:
      if 'acodec' in entry and 'vcodec' in entry:
        if entry['vcodec'] == 'none' or entry['acodec'] == 'DASH audio'or entry['acodec'] == 'none':
          continue
      if 'width' in entry and int(entry['width']) == max_width:
       # logger.debug('found max Audio {} Video {} format {} note {} width {}'.format (entry['acodec'],entry['vcodec'],entry['format'], entry['format_note'],entry['width']) )
        logger.debug('found deep link url: {}'.format(entry['url']) )
        url = entry['url']
      
  return url


file_formats = (
                'mp4',
                'mkv',
                'mp3',
                'opus',
                'ogg',
                'webm',
                'm4a'
                )

file_extension = args.url.rsplit('.',1)[1]

url = args.url

if file_extension.lower() not in file_formats:
  logging.debug ('Unkown file_extension {}'.format (url) )
  url = run_youtube_dl (url)

###
# gnerating json 
###

data = {
  "jsonrpc" : "2.0",
  "id"      : 1,
  "method"  : "Player.Open",
  "params"  : {"item":
                {"file": url}
              },
     
}

data_add = {
  "jsonrpc" : "2.0",
  "id"      : 1,
  "method"  : "Playlist.Add",
  "params"  : {
               "playlistid":1,
               "item":
                 {"file": url} 
            }
}


data_append = {
  "jsonrpc" : "2.0",
  "id"      : 1,
#  "method"  : "Player.Open",
  "method"    : "Playlist.Add",
  "params"  : {"item":
                {"file": url},
                "playlistid" :0 
              },
}





jsonData = json.dumps(data)
hostNport ="http://"+args.host+":"+args.port+"/jsonrpc"

###
# send url to kodi 
###

logger.debug ("Sending {} to {}\n{}".format(url,hostNport,jsonData) ) 
r = requests.post(hostNport, data = jsonData)

logger.debug (r.content)

answer =  json.loads  (str(r.content,'utf8' ) )

if answer['result'] == 'OK':
  logger.info('succesfully send {} to {}'.format(args.url,args.host))
else:
  logger.warning('Error sending {} to {}'.format(args.url,args.host))

