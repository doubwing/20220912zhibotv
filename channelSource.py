import json
import os
import M3UChecker

SEPERATOR = os.sep

def getJSONFileInfoByKey(filePath, key):
    with open(filePath, 'r', encoding='utf8') as file:
        jsonFile = json.load(file)
    return jsonFile[key]

def getChannelURL(channelFileDir):
    urlArr = []
    for filePath in os.listdir(channelFileDir):
        if filePath.endswith("m3u"):
            os.remove(f"{channelFileDir}{SEPERATOR}{filePath}")
            continue
        channelUrl = getJSONFileInfoByKey(f"{channelFileDir}{SEPERATOR}{filePath}{SEPERATOR}request.json", "url")
        urlArr.append(channelUrl)
    with open(f"{channelFileDir}{SEPERATOR}channelUrl.m3u", "w") as file:
        for line in urlArr:
            file.write(f"#EXTINF:-1 group-title=\"test\",test\n")
            file.write(f"{line}\n")

basePath = "/home/easul/Desktop/test"
getChannelURL(basePath)
M3UChecker.checkChannelsBySomePath(f'{basePath}{SEPERATOR}channelUrl.m3u', f'{basePath}{SEPERATOR}usefulChannel.m3u', 
    f'{basePath}{SEPERATOR}uselessChannel.m3u', 1)  
