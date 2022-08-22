import getopt
import json
import os
import re
import shutil
import sys
import time
import zipfile
import M3UChecker

SEPERATOR = os.sep
HELP = '''
该脚本用于HttpCanary打包zip或其他订阅源的操作

-h help     :获取帮助
-f file     :指定要操作的zip包路径
             zip包格式样例:上海卫视_上海总.zip，将自动从其中获取频道名和频道组
             zip包格式样例:上海卫视.zip，将自动从其中获取频道名，频道组自动判断
-d dir      :指定要操作的多个zip包所在路径，用于多个视频源的抓取
             zip包格式样例:上海卫视_上海总.zip，将自动从其中获取频道名和频道组
             zip包格式样例:上海卫视.zip，将自动从其中获取频道名，频道组自动判断
-n name     :该频道源的名称
-g group    :该频道所属组名称
-c change   :将`北京卫视, http://xxxx`的格式转为m3u8，频道组自动判断

示例
1. 获取帮助
python3 channelSource.py -h
2. 操作zip包
有效源与无效源将在.`/output/source/年_月_日_时_分_秒`目录下生成
2.1 从zip包名获取频道名与频道组
python3 channelSource.py -f /home/xxx/Desktop/test/上海卫视_上海总.zip
2.2 从zip包名获取频道名，频道组自动判断
python3 channelSource.py -f /home/xxx/Desktop/test/上海卫视.zip
2.3 zip包名并没有任何含义，则从参数获取频道名与频道组
python3 channelSource.py -f /home/xxx/Desktop/test/test.zip -n 上海卫视 -g 上海总
3. 操作多个zip包，文件夹下有多个zip包
有效源与无效源将在.`/output/source/年_月_日_时_分_秒`目录下生成
python3 channelSource.py -d /home/xxx/Desktop/test/
4. 改换`北京卫视, http://xxxx`格式的视频源文件到m3u
文件生成到该文件目录下，为`InM3u8.m3u`的后缀
python3 channelSource.py -c /home/xxx/Desktop/test/test.m3u
'''
WRONG = "参数输入错误"
# 排除从网站抓取的源
WRONG_M3U8_REGEXX = "v2.91kds.cn"
CURRENT_TIME = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())


def createDirIfNotExists(basePath):
    if not os.path.exists(basePath):
        os.makedirs(basePath)

def getJSONFileInfoByKey(filePath, key):
    with open(filePath, 'r', encoding='utf8') as file:
        jsonFile = json.load(file)
    return str(jsonFile[key])

def extractChannelSourceZipFile(channelSourceZipFile, basePath):
    file = zipfile.ZipFile(channelSourceZipFile)
    file.extractall(basePath)
    file.close()

def getChannelGroupName(channelName: str, channelGroup: str = None):
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
    gangaotaiTVRegex = r"凤凰卫视中文台|凤凰卫视咨询台"
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
    elif re.search(gangaotaiTVRegex, channelName, re.I) != None:
        channelGroup = "港澳台总"
    elif re.search("卫视", channelName, re.I) != None:
        channelGroup = channelName[:channelName.find("卫视")] + "总"
    elif re.search("NewTV", channelName, re.I) != None:
        channelGroup = "NewTV"
    else:
        channelGroup = "默认"

    return channelGroup

def saveChannelM3u8URL(channelFileDir:str, channelSavePath: str, channelName: str, channelGroup:str):
    urlSet = set()
    for filePath in os.listdir(channelFileDir):
        channelURL = getJSONFileInfoByKey(f"{channelFileDir}{SEPERATOR}{filePath}{SEPERATOR}request.json", "url")
        if channelURL.find(".m3u8") != -1 and re.search(WRONG_M3U8_REGEXX, channelURL) == None:
            urlSet.add(channelURL)

    with open(channelSavePath, "w") as file:
        for line in urlSet:
            file.write(f"#EXTINF:-1 group-title=\"{channelGroup}\",{channelName}\n")
            file.write(f"{line}\n")

# 手机电视直播
# https://shouji.baidu.com/detail/4034015
# 需HttpCanary抓包某频道源后获取
def getShouJiDianShiZhiBoChannelM3u(channelSourceZipFile, channelName, channelGroup, isChannelSourceDir = False):
    basePath = os.getcwd() 
    tempPath = basePath + f"{SEPERATOR}temp_channel_dir"
    middlePath = '' if not isChannelSourceDir else f'{SEPERATOR}{CURRENT_TIME}'
    outputPath = basePath + f"{SEPERATOR}output{SEPERATOR}source{middlePath}"
    channelGroup = getChannelGroupName(channelName, channelGroup)
    channelTempSavePath = f'{tempPath}{SEPERATOR}channelURL.m3u'
    usefulChannelPath = f'{outputPath}{SEPERATOR}{channelName}_{channelGroup}_usefulChannel.m3u'
    uselessChannelPath = f'{outputPath}{SEPERATOR}{channelName}_{channelGroup}_uselessChannel.m3u'
    if os.path.exists(tempPath):
        shutil.rmtree(tempPath)
    createDirIfNotExists(tempPath)
    createDirIfNotExists(outputPath)
    extractChannelSourceZipFile(channelSourceZipFile, tempPath)
    saveChannelM3u8URL(tempPath, channelTempSavePath, channelName, channelGroup)
    M3UChecker.checkChannelsBySomePath(channelTempSavePath, usefulChannelPath, uselessChannelPath, 1)
    shutil.rmtree(tempPath)
    print("可用频道源在如下路径")
    print(f'{outputPath}{SEPERATOR}usefulChannel.m3u')
    print("不能访问频道源在如下路径，可能有部分源存在误判情况")
    print(f'{outputPath}{SEPERATOR}uselessChannel.m3u')

def changeChannelFileToM3u8(filePath: str):
    fileInM3u8 = filePath.replace(".m3u", "InM3u8.m3u")
    with open(fileInM3u8, "w", encoding="utf8") as file:
        file.write("#EXTM3U\n")
    with open(filePath, "r", encoding="utf8") as r, open(fileInM3u8, "a", encoding="utf8") as w:
        for line in r:
            channelName, channelURL = line.split(",")
            channelGroupName = getChannelGroupName(channelName)
            w.write(f'#EXTINF:-1 group-title="{channelGroupName}",{channelName}\n')
            w.write(f'{channelURL}')

if __name__ == "__main__":
    # 参考：https://www.jb51.net/article/198726.htm
    channelSourceZipFile = ''
    channelName = ''
    channelGroupName = ''
    channelSourceZipFileDir = ''
    try:
        opts, args = getopt.getopt(sys.argv[1: ], "hf:n:g:d:c:", ["help", "file=", "name=", "group=", "dir=", "change="])
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
        if opt == "-d" or opt == "--dir":
            channelSourceZipFileDir = arg
        if opt == "-c" or opt == "--change":
            changeChannelFileToM3u8(arg)
            sys.exit(0)

    if channelSourceZipFileDir == '':
        if channelSourceZipFile == '':
            print("请输入频道源zip文件后再继续下列操作")
            sys.exit(0)

        if not os.path.exists(channelSourceZipFile):
            print("zip文件不存在，请重新输入")
            sys.exit(0)

        zipFileName = channelSourceZipFile.split(SEPERATOR)[-1]
        if zipFileName.find("_") != -1:
            channelName, channelGroupName = zipFileName.split("_")
            channelGroupName = channelGroupName.split(".")[0]
        else:
            if channelName == '':
                print("请输入频道名称和频道源zip文件后再继续下列操作")
                sys.exit(0)
            if channelGroupName == '':
                print("未输入频道所属组的名称，将通过频道名称自动判断所属组信息")
        getShouJiDianShiZhiBoChannelM3u(channelSourceZipFile, channelName, channelGroupName)
        sys.exit(0)
    
    if not os.path.isdir(channelSourceZipFileDir):
        print("zip文件夹路径输入错误，请重新输入")
        sys.exit(0)
    
    for zipFile in os.listdir(channelSourceZipFileDir):
        channelSourceZipFile = f"{channelSourceZipFileDir}{SEPERATOR}{zipFile}"
        if zipFile.find("_") != -1:
            channelName, channelGroupName = zipFile.split("_")
            channelGroupName = channelGroupName.split(".")[0]
        else:
            channelName = zipFile
        getShouJiDianShiZhiBoChannelM3u(channelSourceZipFile, channelName, channelGroupName, True)