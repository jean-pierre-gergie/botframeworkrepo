import requests

class DirectLineAPI(object):
    def __init__(self,direct_line_secret):
        self.direct_line_secret = direct_line_secret
        self.base_url = 'https://directline.botframework.com/v3/directline'
        self.headers = None



    def set_headers(self):
        headers = {'Content-Type': 'application/json'}
        value = ' '.join(['Bearer', self.direct_line_secret])
        headers.update({'Authorization': value})
        self.headers = headers
        print(headers)

    def generate_token(self):
        url = '/'.join([self.base_url, 'tokens/generate'])
        bot_response = requests.post(url, headers=self.headers)
        json_response = bot_response.json()
        print("generate token response"
              "here it is")
        print(json_response)
        if 'error' in json_response:
            print("NO token")
        else:
            self.token = json_response['token']

    def start_conversation(self):
        url = '/'.join([self.base_url, 'conversations'])
        # this is actually optional
        # json_payload = {
        #     'locale': 'en-EN',
        #     'type': 'message',
        #     'from': {'id': 'user1'},
        #     'text':"string"
        # }
        bot_response = requests.post(url, headers=self.headers)
        print("here is the request")
        print(str(requests.post(url, headers=self.headers)))
        json_response = bot_response.json()
        print("start conversation  response"
              "here it is")
        print(json_response)
        if 'error' in json_response:
            print("conversationid not available [request failed]")
        else:
            print(f"conversationid available [request succeeded]")
            self.conversationid = json_response['conversationId']

    def send_message(self, text):
        url = '/'.join([self.base_url, 'conversations', self.conversationid, 'activities'])
        print("send message url")
        print(url)
        json_payload = {
            'locale': 'en-EN',
            'type': 'message',
            'from': {'id': 'user1'},
            'text': text
        }
        bot_response = requests.post(url, headers=self.headers, json=json_payload)
        if bot_response.status_code == 200:
            return "message sent"
        return "error contacting bot"

    def get_message(self):
        """Get a response message back from the botframework using directline api"""
        url = '/'.join([self.base_url, 'conversations', self.conversationid, 'activities'])
        bot_response = requests.get(url, headers=self.headers,json={'conversationId': self.conversationid})

        if bot_response.status_code == 200:
            json_response = bot_response.json()
            print(json_response)

            return json_response['activities'][1]['text']
        return "error contacting bot for response"







