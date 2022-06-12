import re

def loadM3uFile(m3uFile): 
    channel = []
    with open(m3uFile, 'r', encoding='utf8') as file:
        channelInfo = ''
        channelUrl = ''
        for line in file:
            if line.startswith('#EXTINF:-1'):
                channelInfo = line.replace('\n', '')
            if line.startswith('http'):
                channelUrl = line.replace('\n', '')
                channel.append((channelInfo, channelUrl))
        return channel

def deleteSuffixAfterChannelInfo(channel):
    for index, channelItem in enumerate(channel):
        channelInfo = channelItem[0]
        if str(channelInfo).find('（源') != -1:
            channelInfo = re.sub(r'（源.*?）', '', channelInfo)
        channel[index] = (channelInfo, channelItem[1])
    return channel

def addSuffixAfterChannelInfo(channel):
    currentChannel = ''
    channelCount = 1
    for index, channelItem in enumerate(channel):
        channelInfo = channelItem[0]
        if channelInfo == currentChannel:
            channelCount = channelCount + 1
        else:
            currentChannel = channelInfo
            channelCount = 1
        if str(channelInfo).find('（源') == -1:
            channelInfo = channelInfo + '（源' + str(channelCount) + '）'
            channel[index] = (channelInfo, channelItem[1])
    return channel

def writeM3uInfoToFile(channel, outputM3uFile): 
    with open(outputM3uFile, 'w', encoding='utf8') as file:
        file.write('#EXTM3U\n')
        for channelItem in channel:
            file.write(channelItem[0] + '\n')
            file.write(channelItem[1] + '\n')

def addSuffix(originFile, outputFile):
    channel = addSuffixAfterChannelInfo(loadM3uFile(originFile))
    writeM3uInfoToFile(channel, outputFile) 

def delSuffix(originFile, outputFile):
    channel = deleteSuffixAfterChannelInfo(loadM3uFile(originFile))
    writeM3uInfoToFile(channel, outputFile) 

if __name__ == '__main__':
    # 给直播源添加后缀“（源1）”
    addSuffix('./test.m3u', './newTest.m3u')
    # 删除直播源后缀
    # delSuffix('./newTest.m3u', './newTest2.m3u')