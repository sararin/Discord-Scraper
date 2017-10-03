import urllib2, json

settings = {
    'Token': '<TOKEN>',
    'ServerID': '<SERVERID>',
    'ChannelID': '<CHANNELID>',
    'Query': 'has=image&has=video&include_nsfw=true'
}

def grabJSON():
    opener = urllib2.build_opener()
    opener.addheaders = [
        ('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36 OPR/48.0.2685.32'),
        ('authorization', settings['Token'])
    ]
    urllib2.install_opener(opener)

def grabData(location, filename):
    newopener = urllib2.build_opener()
    newopener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36 OPR/48.0.2685.32')]
    urllib2.install_opener(newopener)

    try:
        imgdata = urllib2.urlopen(location).read()

        try:
            with open(filename, 'wb') as f: f.write(imgdata)
        except IOError, e:
            print e
            
    except urllib2.HTTPError, e:
        print '{}: {}'.format(e, imgurl)

    

if __name__ == '__main__':
    pages = input('Enter number of pages to grab: ')
    for x in xrange(pages):
        grabJSON()
        url = 'https://discordapp.com/api/v6/guilds/{}/messages/search?{}&channel_id={}&offset={}'.format(settings['ServerID'], settings['Query'], settings['ChannelID'], (25*x))

        try:
            read = urllib2.urlopen(url).read()
            data = json.loads(read)

            for messages in data['messages']:
                for x in xrange(len(messages)):
                    for attachments in messages[x]['attachments']:
                        location = attachments['url']
                        filename = '{}.{}'.format(location.split('/')[-2], location.split('.')[-1])
                        grabData(location, filename)
                        
        except urllib2.HTTPError, e:
            print e
