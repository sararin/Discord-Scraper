from urllib3 import disable_warnings, exceptions
from requests import get, post, delete, codes
from random import randrange as rand
from os import path, mkdir, getcwd
from threading import Thread as th
from json import loads as toarr
from shutil import copyfileobj
from sys import stdout

disable_warnings(exceptions.InsecureRequestWarning)
charset = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
rstring = lambda length: [charset[rand(0, len(charset)-1)] for x in range(length)]

class Discord:
    def __init__(self, token, server, channel):
        self.agent   = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.0.300 Chrome/56.0.2924.87 Discord/1.6.15 Safari/537.36'
        self.channel = channel
        self.server  = server
        self.token   = token
        self.query   = ''

    def setQuery(self, isNSFW=True, hasLink=False, hasEmbed=False, hasFile=False, hasVideo=False, hasImage=True, hasSound=False):
        if isNSFW: self.query   = 'include_nsfw=true'
        if hasLink: self.query  =  '{}&has=link'.format(self.query)
        if hasEmbed: self.query = '{}&has=embed'.format(self.query)
        if hasFile: self.query  =  '{}&has=file'.format(self.query)
        if hasVideo: self.query = '{}&has=video'.format(self.query)
        if hasImage: self.query = '{}&has=image'.format(self.query)
        if hasSound: self.query = '{}&has=sound'.format(self.query)

    def grabJSON(self, page=0):
        url, header = 'https://discordapp.com/api/v6/guilds/{}/messages/search?{}&channel_id={}&offset={}'.format(self.server, self.query, self.channel, page * 25), {'user-agent': self.agent, 'authorization': self.token}
        jsonContent = get(url, headers=header, verify=False, allow_redirects=False)

        if jsonContent.status_code == codes.ok: return toarr(jsonContent.text)
        else: stdout.write('Failed to grab JSON data from \'{}\'.\n'.format(url))

    def saveFile(self, fileURL, dataPath):
        rawFileData = get(fileURL, stream=True)
        if rawFileData.status_code == codes.ok:
            rawFileName = path.join(dataPath, fileURL.split('/')[-1])
            if path.exists(rawFileName): rawFileName = path.join(dataPath, '{}-{}'.format(''.join(rstring(8)), fileURL.split('/')[-1]))
            with open(rawFileName, 'wb') as fStream: copyfileobj(rawFileData.raw, fStream)
        del rawFileData

if __name__ == '__main__':
    discord = Discord('<TOKEN>', 0, 0)
    discord.setQuery(True, True, True, True, True, True)

    numPages, folderName, dataArray = int(input('Pages to scrape: ')), 'discord_scrapes', []
    dataPath = path.join(getcwd(), folderName)
    if not path.exists(dataPath): mkdir(dataPath)

    for i in range(numPages):
        jsonData = discord.grabJSON(i)

        for messages in jsonData['messages']:
            for x in range(len(messages)):
                for attachments in messages[x]['attachments']: dataArray.append(attachments['url'])

        dataArray, threads = list(set(dataArray)), []
        for data in dataArray:
            t = th(target=discord.saveFile, args=(data, dataPath, ))
            threads.append(t)

        for thread in threads:
            thread.start()
            thread.join()

        del threads[:]
