import requests
import time
import os
from multiprocessing import Pool
from func_timeout import func_set_timeout

def welcome():
    msg = '''
=========================================================================
888b     d888  .d8888b.  888     888      88888888888                888 
8888b   d8888 d88P  Y88b 888     888          888                    888 
88888b.d88888      .d88P 888     888          888                    888 
888Y88888P888     8888"  888     888          888   .d88b.   .d88b.  888 
888 Y888P 888      "Y8b. 888     888          888  d88""88b d88""88b 888 
888  Y8P  888 888    888 888     888          888  888  888 888  888 888 
888   "   888 Y88b  d88P Y88b. .d88P          888  Y88..88P Y88..88P 888 
888       888  "Y8888P"   "Y88888P"           888   "Y88P"   "Y88P"  888
=========================================================================
'''
    return msg

# https://blog.csdn.net/Chenkeyu_/article/details/118354931
@func_set_timeout(3)
def get(url,GetStatus=0):
    headers = {
        'Accept-Language': "zh-CN,zh",
        'User-Agent': "Mozilla/5.0 (Linux; U; Android 8.1.0; zh-cn; BLA-AL00 Build/HUAWEIBLA-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/8.9 Mobile Safari/537.36",
        'Accept-Encoding': "gzip"
    }
    try:
        res = requests.request("GET", url, headers=headers, timeout=3)  #此处设置超时时间
    except:
        return 0
    if GetStatus == 1:
        return res.status_code
    else:
        if res.status_code == 200:
            res = str(res.content,'utf-8')
        else:
            res = 0
        return res

def checkLink(url):
    try:
        res = get(url,1)
    except:
        return 1
    if res == 200:
        return 1
    else:
        return 0

def displayMsg(workname='Default',msg=''):
    now = time.asctime( time.localtime(time.time()) )
    print(f'{now} - {workname}: ' + msg)

def writeFile(filename,content):
    with open(filename,'w',encoding='utf8') as file:
        file.write(content)

def endWith(fileName, *endstring):
    array = map(fileName.endswith, endstring)
    if True in array:
        return True
    else:
        return False

def m3u_filelist(path):
    fileList = os.listdir(path)
    files = []
    for filename in fileList:
        if endWith(filename, '.m3u'):
            files.append(filename)  # 所有m3u文件列表
    return files


def m3u_load(m3uFile):
    channel = []
    errorNum = 0
    status = 0   # 实时改变步骤状态
    with open(m3uFile, 'r', encoding='utf8') as file:
        displayMsg('m3u_load', f'当前载入列表：{m3uFile}')
        for line in file:
            # 如果当前是描述行：
            if line.startswith('#EXTINF:-1'):
                if status !=0:
                    displayMsg('m3u_load', f'{m3uFile}当前列表缺少行')
                    errorNum+=1
                    exit()
                channelInfo = str(line).replace('\n','')
                status = 1

            # 如果当前是URL行
            if line.startswith('http') or line.startswith('rtsp'): # 当前行为URL
                if status != 1:
                    displayMsg('m3u_load', f'{m3uFile}当前列表缺少行')
                    errorNum += 1
                    exit()
                channelUrl = str(line).replace('\n','')
                channel.append((channelInfo, channelUrl))
                status = 2
            # 上述判断完成
            if status == 2: # 上述步骤处理完毕
                status = 0
        displayMsg('m3u_load', f'{m3uFile} 解析完毕')
        return channel

def work(m3u_data,outputFile,workname='Default',wrongFile = 'wrong.m3u'):
    displayMsg(workname, f'总数据量为{len(m3u_data)}个')
    new_data = []
    wrong_data = []
    for data in m3u_data:
        txt1 = data[0].split(',') # 分割节目名称与标签属性
        name = txt1[1] # 电视名称
        url= data[1] # 播放链接
        if checkLink(url):
            new_data.append(data)
            displayMsg(workname, f'{name} 访问成功')
        else:
            wrong_data.append(data)
            displayMsg(workname, f'{name} 【失败】！')
        if len(new_data) >= 100:
            with open(outputFile, 'a',encoding='utf8') as file:
                for item in new_data:
                    file.write(item[0] + '\n')
                    file.write(item[1] + '\n')
                new_data.clear()
    with open(outputFile, 'a',encoding='utf8') as file:
        for item in new_data:
            file.write(item[0] + '\n')
            file.write(item[1] + '\n')
    with open(wrongFile, 'a',encoding='utf8') as file:
        for item in wrong_data:
            file.write(item[0] + '\n')
            file.write(item[1] + '\n')
    
    return outputFile

# 读取当前目录.m3u文件，并去除checkOutput.m3u
# 依次检测链接是否可用，可用链接放到checkOutput.m3u，可能不可用链接放到wrong.m3u
# if __name__ == '__main__':
def checkChannelsFromCurrentDir():
    print(welcome())

    outputFile = 'checkOutput.m3u'

    displayMsg('Master','开始读取文件列表：')
    fileList = m3u_filelist(os.getcwd())
    
    if outputFile in fileList: # 除去输出文件本身
        fileList.remove(outputFile)

    writeFile(outputFile,'#EXTM3U\n')

    p = Pool(1)
    for file in fileList:
        p.apply_async(work, args=(m3u_load(file),outputFile,file))
    p.close()
    p.join()

def checkChannelsBySomePath(checkFile, outputFile, uselessFile, threadNumber):
    currentTime = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
    writeFile(outputFile,f'#EXTM3U\n#{currentTime}\n')
    writeFile(uselessFile,f'#EXTM3U\n#{currentTime}\n')
    m3u_data = m3u_load(checkFile)
    singleTaskNumber = len(m3u_data) // threadNumber
    outputFiles = []
    p = Pool(threadNumber)
    for index in range (threadNumber):
        if index == threadNumber - 1:
            result = p.apply_async(work, args=(m3u_data[index * singleTaskNumber: ],outputFile + str(index),
                checkFile + '--' + str(index),uselessFile))
        else:
            result = p.apply_async(work, args=(m3u_data[index * singleTaskNumber: (index + 1) * singleTaskNumber],outputFile  + str(index),
                checkFile + '--' + str(index),uselessFile))
        outputFiles.append(result)
    p.close()
    p.join()
   
    for filePath in outputFiles:
        with open(filePath.get(), 'r',encoding='utf8') as origin, open(outputFile, 'a',encoding='utf8') as dest :
            dest.write(origin.read())
        os.remove(filePath.get())

