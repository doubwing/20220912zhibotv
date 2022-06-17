import M3UChecker
import re

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

def deleteSuffixAfterChannelInfo(channel):
    for index, channelItem in enumerate(channel):
        channelGroup = channelItem[0]
        channelName = channelItem[1]
        channelUrl = channelItem[2]
        if channelUrl == '' or channelName == '':
            continue
        channelInfo = '#EXTINF:-1 group-title="' + channelGroup + '",' + channelName
        channel[index] = (channelInfo, channelUrl)
    return channel

def addSuffixAfterChannelInfo(channel):
    currentChannelGroup = ''
    currentChannelName = ''
    channelCount = 1
    for index, channelItem in enumerate(channel):
        channelGroup = channelItem[0]
        channelName = channelItem[1]
        channelUrl = channelItem[2]
        if channelUrl == '' or channelName == '':
            continue
        if channelGroup == currentChannelGroup and channelName == currentChannelName:
            channelCount = channelCount + 1
        else:
            currentChannelGroup = channelGroup
            currentChannelName = channelName
            channelCount = 1
        channelInfo = '#EXTINF:-1 group-title="' + channelGroup + '",' + channelName + '（源' + str(channelCount) + '）'
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
    writeM3uInfoToFile(deleteSuffixAfterChannelInfo(originChannels), outputFile) 
    
def writeM3uInfoToFile(channel, outputM3uFile): 
    with open(outputM3uFile, 'w', encoding='utf8') as file:
        file.write('#EXTM3U\n')
        for channelItem in channel:
            if len(channelItem) == 2:
                file.write(channelItem[0] + '\n')
                file.write(channelItem[1] + '\n')

# 给直播源添加后缀“（源1）”
def addSuffix(originFile, outputFile):
    channel = addSuffixAfterChannelInfo(loadM3uFile(originFile))
    writeM3uInfoToFile(channel, outputFile) 

# 删除直播源后缀
def delSuffix(originFile, outputFile):
    channel = deleteSuffixAfterChannelInfo(loadM3uFile(originFile))
    writeM3uInfoToFile(channel, outputFile) 

if __name__ == '__main__':
    # 给直播源添加新源，去重并添加后缀“（源1）”
    # 合并新源并去除重复源
    print('合并新源并去除重复源')
    combineChannelInfo('./频道源/originChannel.m3u', './输出/outputChannel.m3u', './频道源/newChannel.m3u') 
    # 检查直播源有效性
    print('源有效性检测')
    M3UChecker.checkChannelsBySomePath('./输出/outputChannel.m3u', './输出/usefulChannel.m3u', 
        './输出/uselessChannel.m3u', 40)   
    # 给直播源添加后缀“（源1）”
    print('添加源后缀')
    addSuffix('./输出/usefulChannel.m3u', './输出/usefulChannelWithSuffix.m3u')     
    # 删除直播源后缀
    # print('源后缀去除')
    # delSuffix('./输出/usefulChannelWithSuffix.m3u', './输出/outputChannelWithoutSuffix.m3u')