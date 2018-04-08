import threading, requests, urllib3, shutil, json, sys, os
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Discord:
    def __init__(self):
        self.token      = '<TOKEN>'
        self.server     = '<SERVER ID>'
        self.channel    = '<CHANNEL ID>'
        self.query      = 'has=image&has=video&include_nsfw=true'

    def grabJSON(self, page=0):
        url, header = 'https://discordapp.com/api/v6/guilds/{}/messages/search?{}&channel_id={}&offset={}'.format(self.server, self.query, self.channel, page * 25), {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.0.300 Chrome/56.0.2924.87 Discord/1.6.15 Safari/537.36', 'authorization': self.token}
        jsonContents = requests.get(url, headers=header, verify=False, allow_redirects=False)

        if jsonContents.status_code == requests.codes.ok:
            requests.encoding = 'utf-8'
            return json.loads(jsonContents.text)
        else: sys.stdout.write('Failed to grab JSON data from \'{}\'.\n'.format(url))

    def saveFile(self, fileUrl, dataPath):
        rawFileData = requests.get(fileUrl, stream=True)
        if rawFileData.status_code == requests.codes.ok:
            rawFileName = os.path.join(dataPath, fileUrl.split('/')[-1])
                    
            with open(rawFileName, 'wb') as fileStream:
                shutil.copyfileobj(rawFileData.raw, fileStream)
                        
        del rawFileData

if __name__ == '__main__':
    discord = Discord()
    
    numPages, folderName, dataArray = int(input('Pages to scrape: ')), 'discord_scrapes', []
    dataPath = os.path.join(os.getcwd(), folderName)
    if not os.path.exists(dataPath): os.mkdir(dataPath)

    for i in range(numPages):
        jsonData = discord.grabJSON(i)

        for messages in jsonData['messages']:
            for x in range(len(messages)):
                for attachments in messages[x]['attachments']:
                    dataArray.append(attachments['url'])

    dataArray, threads = list(set(dataArray)), []
    for data in dataArray:
        t = threading.Thread(target=discord.saveFile, args=(data, dataPath, ))
        threads.append(t)

    for thread in threads:
        thread.start()

        if not thread.isAlive:
            threads.remove(thread)

    del threads[:]
