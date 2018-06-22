import http.client, random, json, os

# Generate random characters for when there are duplicate filenames.
charset = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
random_string = lambda length: [random.choice(charset) for x in range(length)]

# Discord class
class Discord:

    # Constructor
    def __init__(self):
        self.token      = '<TOKEN>'
        self.server     = '<SERVER ID>'
        self.channel    = '<CHANNEL ID>'
        self.query      = ''
        self.jsondata   = []

    # Generate query
    def new_query(self, is_nsfw=True, has_image=True, has_video=True):
        self.query = 'include_nsfw=true' if is_nsfw else self.query
        self.query = '{}&has=image'.format(self.query) if has_image else self.query
        self.query = '{}&has=video'.format(self.query) if has_video else self.query

    # Grab JSON from the Discord search function
    def grab_json(self, pages=1):
        for i in range(0, pages):
            conn = http.client.HTTPSConnection('discordapp.com', 443)
            conn.request('GET', '/api/v6/guilds/{}/messages/search?{}&channel_id={}&offset={}'.format(self.server, self.query, self.channel, i*25), headers={'authorization': self.token})
            self.jsondata.append(conn.getresponse().read().decode('utf-8'))

    # Sort through the JSON data and pick out the images and then download them
    def grab_files(self):

        # Determine if download path exists; otherwise create it
        download_path = os.path.join(os.getcwd(), 'discord_scrapes')
        if not os.path.exists(download_path): os.mkdir(download_path)

        # Time to traverse through the JSON data
        for json_data in self.jsondata:
            json_data = json.loads(json_data)

            # Time to traverse through the messages
            for message in json_data['messages']:
                try:
                    file_url, file_name, file_size = message[0]['attachments'][0]['url'], os.path.join(download_path, message[0]['attachments'][0]['filename']), message[0]['attachments'][0]['size']
                    if os.path.exists(file_name): file_name = os.path.join(download_path, '{}_{}'.format(''.join(random_string(8)), message[0]['attachments'][0]['filename']))
                    
                    # Download the image file
                    conn = http.client.HTTPSConnection('cdn.discordapp.com', 443)
                    conn.request('GET', '/{}'.format('/'.join(file_url.split('/')[3::])))
                    with open(file_name, 'wb') as fstream:
                        fstream.write(conn.getresponse().read(file_size))
                except IndexError:
                    continue

# Connect to the class and carry out the necessary functions
if __name__ == '__main__':
    discord = Discord()
    discord.new_query()
    discord.grab_json(input('Number of pages to grab: '))
    discord.grab_files()
    
