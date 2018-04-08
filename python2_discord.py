import threading, urllib2, random, json, sys, os

def RandomString(length=5):
    charset, output = 'abcdefghijklmnopqrstuvwxyz0123456789', ''
    for i in range(length): output = output + charset[random.randrange(0, len(charset)-1)]
    return output

class Discord:
    def __init__(self):
        self.token      = '<TOKEN>'
        self.server     = '<SERVER ID>'
        self.channel    = '<CHANNEL ID>'
        self.query      = 'has=image&has=video&include_nsfw=true'

    def grabJSON(self, page=0):
        url, opener = 'https://discordapp.com/api/v6/guilds/{}/messages/search?{}&channel_id={}&offset={}'.format(self.server, self.query, self.channel, page * 25), urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.0.300 Chrome/56.0.2924.87 Discord/1.6.15 Safari/537.36'), ('authorization', self.token)]
        urllib2.install_opener(opener)

        try:
            jsonContents = urllib2.urlopen(url)
            return json.loads(jsonContents.read())
        except: sys.stdout.write('Failed to grab JSON data from \'{}\'.\n'.format(url))

    def saveFile(self, fileUrl, dataPath):
        try:
            rawFileData, rawFileName = urllib2.urlopen(fileUrl).read(), os.path.join(dataPath, fileUrl.split('/')[-1])

            if os.path.exists(rawFileName): rawFileName = os.path.join(dataPath, '{}-{}'.format(RandomString(8), fileUrl.split('/')[-1]))
            with open(rawFileName, 'wb') as fileStream:
                fileStream.write(rawFileData)

            del rawFileData
        except: ''

if __name__ == '__main__':
    discord = Discord()

    numPages, folderName, dataArray = input('Pages to scrape: '), 'discord_scrapes', []
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
        thread.join()

    del threads[:]
