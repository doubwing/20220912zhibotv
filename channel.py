import os
import platform
import time
import M3UChecker
import re

SEPERATOR = os.sep

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

def combineChannelInfo(originFile, outputFile, newFile):
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
    currentTime = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
    with open(outputM3uFile, 'w', encoding='utf8') as file:
        file.write('#EXTM3U\n')
        file.write(f'#current time is {currentTime}\n')
        for channelItem in channel:
            if len(channelItem) == 2:
                file.write(channelItem[0] + '\n')
                file.write(channelItem[1] + '\n')

# 给直播源添加后缀“（源1）”
def addSuffix(originFile, outputFile):
    channel = combineChannelGroupAndName(loadM3uFile(originFile), True)
    writeM3uInfoToFile(channel, outputFile) 

# 删除直播源后缀
def delSuffix(originFile, outputFile):
    channel = combineChannelGroupAndName(loadM3uFile(originFile), False)
    writeM3uInfoToFile(channel, outputFile) 

if __name__ == '__main__':
    # 给直播源添加新源，去重并添加后缀“（源1）”
    # 合并新源并去除重复源
    print('合并新源并去除重复源')
    combineChannelInfo(f'.{SEPERATOR}频道源{SEPERATOR}originChannel.m3u', f'.{SEPERATOR}输出{SEPERATOR}outputChannel.m3u', f'.{SEPERATOR}频道源{SEPERATOR}newChannel.m3u') 
    # 检查直播源有效性
    print('源有效性检测')
    M3UChecker.checkChannelsBySomePath(f'.{SEPERATOR}输出{SEPERATOR}outputChannel.m3u', f'.{SEPERATOR}输出{SEPERATOR}usefulChannel.m3u', 
        f'.{SEPERATOR}输出{SEPERATOR}uselessChannel.m3u', 30)   
    # 给直播源添加后缀“（源1）”
    print('添加源后缀')
    addSuffix(f'.{SEPERATOR}输出{SEPERATOR}usefulChannel.m3u', f'.{SEPERATOR}输出{SEPERATOR}usefulChannelWithSuffix.m3u')     
    print('复制有效源到当前目录')
    if platform.system().lower() == 'windows':
        os.system(f"copy .{SEPERATOR}输出{SEPERATOR}usefulChannel.m3u .{SEPERATOR}iptv.m3u")
    else:
        os.system(f"cp .{SEPERATOR}输出{SEPERATOR}usefulChannel.m3u .{SEPERATOR}iptv.m3u")
    # 删除直播源后缀
    # print('源后缀去除')
    # delSuffix(f'.{SEPERATOR}输出{SEPERATOR}usefulChannelWithSuffix.m3u', f'.{SEPERATOR}输出{SEPERATOR}outputChannelWithoutSuffix.m3u')