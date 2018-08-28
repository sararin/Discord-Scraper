import http.client, threading, random, json, html, sys, os
charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
randomString = lambda length: ''.join([random.choice(charset) for x in range(length)])

class MissingValue(Exception):
    def __init__(self, valueName, fileName):
        sys.stderr.write('{} is invalid in {}'.format(valueName, fileName))

class Requests:
    def __init__(self, headers):
        self.headers = headers

    def splitUrl(self, url):
        scheme, blank, self.domain = url.split('/')[0:3]
        query = '/'.join(url.split('/')[3::])
        
        self.port = 80 if scheme == 'http:' else 443
        self.query = '/{}'.format(query)
    
    def get(self, url):
        self.splitUrl(url)
        
        conn = http.client.HTTPConnection(self.domain, 80) if self.port == 80 else http.client.HTTPSConnection(self.domain, 443)
        conn.request('GET', self.query, headers=self.headers)

        resp = conn.getresponse()
        data = resp.read()

        self.status, self.reason, self.raw, self.text = resp.status, resp.reason, data, html.unescape(data.decode('iso-8859-1'))

class DiscordSpider:
    def __init__(self, config='config.json'):
        fileName = os.path.join(os.getcwd(), config)
        
        try:
            if not os.path.exists(fileName): raise FileNotFoundError
            threads = []
            
            with open(fileName, 'r') as configFile:
                configJSON = json.loads(configFile.read())

            if not configJSON['token']: raise MissingValue('Discord Authorization Token', fileName)
            if not configJSON['query']: raise MissingValue('Discord Search Query', fileName)
            if len(configJSON['servers']) == 0: sys.stderr.write('No Servers to Crawl')

            self.httpHeaders = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.0.300 Chrome/56.0.2924.87 Discord/1.6.15 Safari/537.36',
                'authorization': configJSON['token']
            }

            for serverId, v in configJSON['servers'].items():
                for channelId, folderName in configJSON['servers'][serverId].items():
                    if not os.path.exists(os.path.join(os.getcwd(), folderName)): os.mkdir(os.path.join(os.getcwd(), folderName))
                    for offset in range(0, 200):
                        thread = threading.Thread(target=self.grabJSON, args=(folderName, serverId, channelId, configJSON['query'], offset, ))
                        threads.append(thread)

            for thread in threads:
                thread.start()
                thread.join()

            del threads[:]

        except ValueError:
            sys.stderr.write('{} is not a valid JSON file.\n'.format(fileName))
            
        except FileNotFoundError:
            sys.stderr.write('{} can not be found.\n'.format(fileName))
            
        except IOError:
            sys.stderr.write('Failed to read file: {}\n'.format(fileName))

        except MissingValue: pass

    def grabJSON(self, folderName, serverId, channelId, query, offset):
        req, res = Requests(self.httpHeaders), Requests({})
        req.get('https://discordapp.com/api/v6/guilds/{}/messages/search?{}&channel_id={}&offset={}'.format(serverId, query, channelId, offset * 25))
        jsonData = json.loads(req.text)

        imagelinks = []
        for messages in jsonData['messages']:
            for x in range(len(messages)):
                for attachments in messages[x]['attachments']:
                    imagelinks.append(attachments['url'])

        imagelinks = list(set(imagelinks))
        for images in imagelinks:
            res.get(images)

            if res.status == 200:
                fileName = os.path.join(os.getcwd(), folderName, '{}_{}'.format(randomString(8), images.split('/')[-1]))
                with open(fileName, 'wb') as rawFile:
                    rawFile.write(res.raw)

if __name__ == '__main__':
    ds = DiscordSpider()
