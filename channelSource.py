import getopt
import json
import os
import re
import sys
import M3UChecker

SEPERATOR = os.sep
HELP = '''
该脚本用于HttpCanary打包zip的操作

-f file     :指定要操作的zip包路径
-n name     :该频道源的名称
-g group    :该频道所属组名称
'''
WRONG = "参数输入错误"
def extractChannelSourceZipFile(basePath, channelSourceZipFile):
    print()

def getJSONFileInfoByKey(filePath, key):
    with open(filePath, 'r', encoding='utf8') as file:
        jsonFile = json.load(file)
    return jsonFile[key]

def getChannelGroupName(channelName: str, channelGroup: str):
    if channelGroup != None and channelGroup != '':
        return channelGroup

    cctvRegex = r"CCTV|CGTN|中国教育|新华中文|新华英语|中国气象|中央新影|CHC|CBN"
    shanghaiTVRegex = r"东方卫视"
    guangdongTVRegex = r"南方卫视|深圳卫视"
    shandongTVRegex = r"山东教育卫视"
    fujianTVRegex = r"东南卫视|厦门卫视|海峡卫视"
    sichuanTVRegex = r"康巴卫视"
    jilinTVRegex = r"延边卫视"
    hainanTVRegex = r"三沙卫视"
    qinghaiTVRegex = r"安多卫视"
    xinjiangTVRegex = r"兵团卫视"
    shanxiTVRegex = r"农林卫视"
    if re.search(cctvRegex, channelName, re.I) != None:
        channelGroup = "央视"
    elif re.search(shanghaiTVRegex, channelName, re.I) != None:
        channelGroup = "上海总"
    elif re.search(guangdongTVRegex, channelName, re.I) != None:
        channelGroup = "广东总"
    elif re.search(shandongTVRegex, channelName, re.I) != None:
        channelGroup = "山东总"
    elif re.search(fujianTVRegex, channelName, re.I) != None:
        channelGroup = "福建总"
    elif re.search(sichuanTVRegex, channelName, re.I) != None:
        channelGroup = "四川总"
    elif re.search(jilinTVRegex, channelName, re.I) != None:
        channelGroup = "吉林总"
    elif re.search(hainanTVRegex, channelName, re.I) != None:
        channelGroup = "海南总"
    elif re.search(qinghaiTVRegex, channelName, re.I) != None:
        channelGroup = "青海总"
    elif re.search(xinjiangTVRegex, channelName, re.I) != None:
        channelGroup = "新疆总"
    elif re.search(shanxiTVRegex, channelName, re.I) != None:
        channelGroup = "陕西总"
    elif re.search("卫视", channelName, re.I) != None:
        channelGroup = channelName[:channelName.find("channelName") + 1]
    elif re.search("NewTV", channelName, re.I) != None:
        channelGroup = "NewTV"
    else:
        channelGroup = "默认"

    return channelGroup

def getHttpCanaryChanneM3ulURL(channelFileDir, channelName: str):
    urlArr = []
    for filePath in os.listdir(channelFileDir):
        if filePath.endswith("m3u"):
            os.remove(f"{channelFileDir}{SEPERATOR}{filePath}")
            continue
        channelUrl = getJSONFileInfoByKey(f"{channelFileDir}{SEPERATOR}{filePath}{SEPERATOR}request.json", "url")
        urlArr.append(channelUrl)

    channelGroup = getChannelGroupName(channelName)
    with open(f"{channelFileDir}{SEPERATOR}channelUrl.m3u", "w") as file:
        for line in urlArr:
            file.write(f"#EXTINF:-1 group-title=\"{channelGroup}\",{channelName}\n")
            file.write(f"{line}\n")

# 手机电视直播
# https://shouji.baidu.com/detail/4034015
# 需HttpCanary抓包某频道源后获取
def getShouJiDianShiZhiBoChannelM3u(channelSourceZipFile, channelName, channelGroup):
    basePath = os.getcwd()
    extractChannelSourceZipFile(basePath, channelSourceZipFile)
    getHttpCanaryChanneM3ulURL(basePath, channelName, channelGroup)
    M3UChecker.checkChannelsBySomePath(f'{basePath}{SEPERATOR}channelUrl.m3u', f'{basePath}{SEPERATOR}usefulChannel.m3u', 
        f'{basePath}{SEPERATOR}uselessChannel.m3u', 1)  

if __name__ == "__main__":
    # 参考：https://www.jb51.net/article/198726.htm
    channelSourceZipFile = ''
    channelName = ''
    channelGroupName = ''
    try:
        opts, args = getopt.getopt(sys.argv[1: ], "hf:n:g:", ["help", "file=", "name=", "group="])
    except getopt.GetoptError: 
        print(WRONG)
        print(HELP)
        sys.exit(0)

    if len(opts) == 0:
        print(HELP)

    for opt, arg in opts:
        if opt == "-h" or opt == "--help":
            print(HELP)
        if opt == "-f" or opt == "--file":
            channelSourceZipFile = arg
        if opt == "-n" or opt == "--name":
            channelName = arg
        if opt == "-g" or opt == "--group":
            channelGroupName = arg

    if channelName == '' or channelSourceZipFile == '':
        print("请输入频道名称和频道源zip文件后再继续下列操作")
        sys.exit(0)

    if channelGroupName == '':
        print("未输入频道所属组的范围，将通过频道名称自动判断所属组信息")

    getShouJiDianShiZhiBoChannelM3u(channelSourceZipFile, channelName, channelGroupName)