import sys

import requests
sys.path.append("..")
import M3UChecker

def M3UCheckerTest():
    originChannel = './originChannel.m3u'
    originChannelUseful = './originChannelUseful.m3u'
    originChannelUseless = './originChannelUseless.m3u'
    M3UChecker.checkChannelsBySomePath(originChannel, originChannelUseful, originChannelUseless, 1)

def requestTest():
    resp = requests.request("OPTIONS", url="http://120.194.173.75:6060/0.ts", timeout = 1, stream = True)
    print(resp.status_code)

M3UCheckerTest()
# requestTest()