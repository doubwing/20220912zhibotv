import getopt
import os
import platform
import shutil
import sys
import time
import M3UChecker
import re

SEPERATOR = os.sep
CURRENT_TIME = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
WRONG = "参数输入错误"
HELP = '''
该脚本用于m3u源的处理

-h help             :获取帮助
-o origin           :原本存在的源
-n new              :新添加的源，都是m3u格式
-d dir              :指定一个文件夹下的源，会读取该文件夹下带useless的源
   detection-new    :指明检测新源
   detection-origin :指明检测老源
   delete           :删除源中频道名的后缀`（源1）`

示例
1. 获取帮助
python3 channel.py -h
2. 合并老源与新源
无效源将在.`/output/useless/年_月_日_时_分_秒`目录下生成
带后缀(（源1）)的有效源替换到根目录`iptv.m3u`
不带后缀(（源1）)的有效源替换到频道源下，原来的老源将生成.bak文件
2.1 仅合并源，不进行源有效性检测
python3  channel.py -o /home/xxx/Desktop/test/originChannel.m3u -n /home/xxx/Desktop/test/newChannel.m3u
2.2 合并源，并对老源进行有效性检测
python3  channel.py -o /home/xxx/Desktop/test/originChannel.m3u -n /home/xxx/Desktop/test/newChannel.m3u --detection-origin
2.3 合并源，并对新源进行有效性检测
python3  channel.py -o /home/xxx/Desktop/test/originChannel.m3u -n /home/xxx/Desktop/test/newChannel.m3u --detection-new
2.4 合并源，并对老源与新源进行有效性检测
python3  channel.py -o /home/xxx/Desktop/test/originChannel.m3u -n /home/xxx/Desktop/test/newChannel.m3u --detection-origin --detection-new
3. 合并多个新源与老源
无效源将在.`/output/useless/年_月_日_时_分_秒`目录下生成
带后缀(（源1）)的有效源替换到根目录`iptv.m3u`
不带后缀(（源1）)的有效源替换到频道源下，原来的老源将生成.bak文件
3.1 仅合并源，不进行源有效性检测
python3  channel.py -o /home/xxx/Desktop/test/originChannel.m3u -d /home/xxx/Desktop/test1
3.2 合并源，并对老源进行有效性检测
python3  channel.py -o /home/xxx/Desktop/test/originChannel.m3u -d /home/xxx/Desktop/test1 --detection-origin
3.3 合并源，并对新源进行有效性检测
python3  channel.py -o /home/xxx/Desktop/test/originChannel.m3u -d /home/xxx/Desktop/test1 --detection-new
3.4 合并源，并对老源与新源进行有效性检测
python3  channel.py -o /home/xxx/Desktop/test/originChannel.m3u -d /home/xxx/Desktop/test1 --detection-origin --detection-new
4. 删除源中频道名的后缀`（源1）`
文件生成在当前目录下，带`WithoutSuffix.m3u`后缀
python3 channel.py  --delete /home/xxx/Desktop/test/xxx.m3u

'''

def createDirIfNotExists(basePath):
    if not os.path.exists(basePath):
        os.makedirs(basePath)

'''
如果节目是卫视频道，在群组上加上"总"字
去除链接相同的频道
'''
def loadM3uFile(m3uFile): 
    channel = []
    channelUrlSet = set()
    with open(m3uFile, 'r', encoding='utf8') as file:
        channelInfo = ''
        channelUrl = ''
        beforeChannelGroup = ''
        beforeChannelName = ''
        currentChannelGroup = ''
        currentChannelName = ''
        for line in file:
            if line.startswith('#EXTINF:-1'):
                channelInfo = re.match(r"#EXTINF.*?=\"(.*?)\",(.*?)(（源[\d]+）)?\n", line)
                currentChannelGroup = channelInfo.group(1)
                currentChannelName = channelInfo.group(2)
                if currentChannelName.find('卫视') != -1 and currentChannelGroup.find('总') == -1:
                    currentChannelGroup = currentChannelGroup + '总'
            if line.startswith('http'):
                channelUrl = line.replace('\n', '')
                if currentChannelGroup == beforeChannelGroup and currentChannelName != beforeChannelName:
                    channel.append((beforeChannelGroup, beforeChannelName, ''))

                if currentChannelGroup != beforeChannelGroup:
                    channel.append((beforeChannelGroup, '', ''))

                beforeChannelGroup = currentChannelGroup
                beforeChannelName = currentChannelName

                if channelUrl not in channelUrlSet:
                    channelUrlSet.add(channelUrl)
                    channel.append((currentChannelGroup, currentChannelName, channelUrl))
        return channel

def combineChannelGroupAndName(channel, needSuffix):
    currentChannelGroup = ''
    currentChannelName = ''
    channelSourceCount = 1
    suffix = ''
    for index, channelItem in enumerate(channel):
        channelGroup = channelItem[0]
        channelName = channelItem[1]
        channelUrl = channelItem[2]
        if channelUrl == '' or channelName == '':
            continue
        if needSuffix:
            if channelGroup == currentChannelGroup and channelName == currentChannelName:
                channelSourceCount = channelSourceCount + 1
            else:
                currentChannelGroup = channelGroup
                currentChannelName = channelName
                channelSourceCount = 1
            suffix = '（源' + str(channelSourceCount) + '）'

        channelInfo = '#EXTINF:-1 group-title="' + channelGroup + '",' + channelName + suffix
        channel[index] = (channelInfo, channelUrl)
    return channel

def combineChannelInfo(originFile, newFile, outputFile):
    originChannels = loadM3uFile(originFile)
    newChannels = loadM3uFile(newFile)
    for newChannel in newChannels:
        newChannelGroup = newChannel[0]
        newChannelName = newChannel[1]
        newChannelUrl = newChannel[2]
        if originChannels.count((newChannelGroup, newChannelName, newChannelUrl)) == 0:
            try:
                channelIndex = originChannels.index((newChannelGroup, newChannelName, ''))
                originChannels.insert(channelIndex + 1, newChannel)
            except:
                try:
                    channelGroup = originChannels.index((newChannelGroup, '', ''))
                    originChannels.insert(channelGroup + 1, newChannel)
                except:
                    originChannels.append(newChannel)
    writeM3uInfoToFile(combineChannelGroupAndName(originChannels, False), outputFile) 
    
def writeM3uInfoToFile(channel, outputM3uFile): 
    with open(outputM3uFile, 'w', encoding='utf8') as file:
        file.write('#EXTM3U\n')
        file.write(f'#current time is {CURRENT_TIME}\n')
        for channelItem in channel:
            if len(channelItem) == 2:
                file.write(channelItem[0] + '\n')
                file.write(channelItem[1] + '\n')

def combineOriginAndNewChannel(originChannel, newChannel, tempPath, channelUselessPath, isDetectOriginChannel, isDetectNewChannel, isWindows):
    originChannelUseful = f'{tempPath}{SEPERATOR}originChannelUseful.m3u'
    newChannelUseful = f'{tempPath}{SEPERATOR}newChannelUseful.m3u'
    originChannelUseless = f'{tempPath}{SEPERATOR}originChannelUseless.m3u'
    newChannelUseless = f'{tempPath}{SEPERATOR}newChannelUseless.m3u'
    outputPath = f"{tempPath}{SEPERATOR}outputChannel.m3u"
    outputPathWithSuffix = f"{tempPath}{SEPERATOR}outputChannelWithSuffix.m3u"
     # 检查直播源有效性
    print('源有效性检测')
    if isDetectOriginChannel: 
        M3UChecker.checkChannelsBySomePath(originChannel, originChannelUseful, originChannelUseless, 30)  
    else:
        os.mknod(originChannelUseless)
        if isWindows:
            os.system(f"copy {originChannel} {originChannelUseful}")
        else:
            os.system(f"cp {originChannel} {originChannelUseful}")
    if isDetectNewChannel: 
        M3UChecker.checkChannelsBySomePath(newChannel, newChannelUseful, newChannelUseless, 30) 
    else:
        os.mknod(newChannelUseless)
        if isWindows:
            os.system(f"copy {newChannel} {newChannelUseful}")
        else:
            os.system(f"cp {newChannel} {newChannelUseful}")
    # 合并新源并去除重复源
    print('合并新源并去除重复源')
    combineChannelInfo(originChannelUseful, newChannelUseful, outputPath) 
    # 给直播源添加后缀“（源1）”
    print('添加源后缀')
    addSuffix(outputPath, outputPathWithSuffix)     
    print('复制有效源到当前目录')
    if isWindows:
        os.system(f"copy {outputPathWithSuffix} .{SEPERATOR}iptv.m3u")
    else:
        os.system(f"cp {outputPathWithSuffix} .{SEPERATOR}iptv.m3u")
    print('复制无效源到output目录')
    if isWindows:
        os.system(f"copy {newChannelUseless} {channelUselessPath}")
        os.system(f"copy {originChannelUseless} {channelUselessPath}")
    else:
        os.system(f"cp {newChannelUseless} {channelUselessPath}")
        os.system(f"cp {originChannelUseless} {channelUselessPath}")
    print('复制源到频道源')
    if isWindows:
        os.system(f"ren {originChannel} {originChannel}.{CURRENT_TIME}.bak")
        os.system(f"copy {outputPath} {originChannel}")
    else:
        os.system(f"mv {originChannel} {originChannel}.{CURRENT_TIME}.bak")
        os.system(f"cp {outputPath} {originChannel}")

# 给直播源添加后缀“（源1）”
def addSuffix(originFile, outputFile):
    channel = combineChannelGroupAndName(loadM3uFile(originFile), True)
    writeM3uInfoToFile(channel, outputFile) 

# 删除直播源后缀
def delSuffix(originFile, outputFile):
    channel = combineChannelGroupAndName(loadM3uFile(originFile), False)
    writeM3uInfoToFile(channel, outputFile) 

if __name__ == '__main__':
    basePath = os.getcwd() 
    tempPath = basePath + f"{SEPERATOR}temp_channel_dir"
    channelUselessPath = basePath + f"{SEPERATOR}output{SEPERATOR}useless{SEPERATOR}{CURRENT_TIME}"
    tempNewChannel = f"{tempPath}{SEPERATOR}tempNewChannel.m3u"
    originChannel = ''
    newChannel = ''
    newChannelDir = ''
    isDetectNewChannel = False
    isDetectOriginChannel = False
    isWindows = platform.system().lower() == 'windows'

    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:n:d", ["help", "origin=", "new=", "detection-new", "detection-origin", "dir=", "delete="])
    except getopt.GetoptError:
        print(WRONG)
        print(HELP)
        sys.exit(0)

    if len(opts) == 0:
        print(HELP)
        sys.exit(0)
        
    for opt, arg in opts:
        if opt == "-h" or opt == "--help":
            print(HELP)
        if opt == "-o" or opt == "--origin":
            originChannel = arg
        if opt == "-n" or opt == "--new":
            newChannel = arg
        if opt == "--detection-new":
            isDetectNewChannel = True
        if opt == "--detection-origin":
            isDetectOriginChannel = True
        if opt == "-d" or opt == "--dir":
            newChannelDir = arg
        if opt == "--delete":
            # 删除直播源后缀
            print('源后缀去除')
            delSuffix(arg, arg.replace(".m3u", "WithoutSuffix.m3u"))
            sys.exit(0)

    if os.path.exists(tempPath):
        shutil.rmtree(tempPath)
    createDirIfNotExists(tempPath)
    createDirIfNotExists(channelUselessPath)
    
    if newChannelDir == '':
        if originChannel == '' or newChannel == '':
            print("请添加旧源与新源的路径后再操作")
            sys.exit(0)
    else:
        if not os.path.exists(newChannelDir):
            print("新源文件夹不存在，请重新输入")
            sys.exit(0)
        if originChannel == '':
            print("请添加旧源的路径后再操作")
            sys.exit(0)
        with open(tempNewChannel, "w", encoding='utf8') as file:
            file.write("#EXTM3U\n")
        for newChannelFile in os.listdir(newChannelDir):
            if newChannelFile.find("useless") != -1:
                continue
            newChannelFile = f"{newChannelDir}{SEPERATOR}{newChannelFile}"
            with open(newChannelFile, "r") as r, open(tempNewChannel, "a", encoding='utf8') as w:
                for line in r:
                    if line.startswith("#EXTINF") or line.startswith("http"):
                        w.write(line)
        newChannel = tempNewChannel
    combineOriginAndNewChannel(originChannel, newChannel, tempPath, channelUselessPath, isDetectOriginChannel, isDetectNewChannel, isWindows)
    
    shutil.rmtree(tempPath)