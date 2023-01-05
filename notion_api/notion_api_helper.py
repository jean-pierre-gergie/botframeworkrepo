import  requests
import json

class Notion():
    def __init__(self):
        self.titles =[]
        self.apikey = 'secret_MzNkYE11EqQUboEQQeey4ONYK8apE5hxajSZ6DHzqkw'
        self.token= "Bearer " + self.apikey
        self.data_base_id='4e9c5d7b9d124f14a117ddadd24b70bd'
        self.page_id=[]

    async def query_db(self):
        headers = {
            'Authorization': self.token,
            'Notion-Version': '2022-06-28',
            'Content-Type': 'application/json',
        }
        data = {
            "filter": {
                "property": "Status",
                "select": {
                    "equals": "To Do"
                }
            }
        }
        data = str(data)
        data = data.replace("'", '"')

        url = 'https://api.notion.com/v1/databases/'+self.data_base_id +'/query'

        response = requests.post(url, headers=headers,data=data)
        jsonResponse = response.json()
        # print("query data base: ")
        # print(jsonResponse)
        for element in jsonResponse['results']:
            self.page_id.append(element['id'])

        await self.retrieve_title()


    async def retrieve_title(self):
        for page_id in self.page_id:
            jsonResponse = await self.req(page_id)

            for element in jsonResponse['results']:
                self.titles.append(element['title']['text']['content'])
                # print(element['title']['text']['content'])
        return

    async def req(self, page_id: str):

        headers = {
            'Authorization': self.token,
            'Notion-Version': '2022-06-28',

        }
        url = 'https://api.notion.com/v1/pages/' + page_id + '/properties/' + 'title'
        response = requests.get(url, headers=headers)
        jsonResponse = response.json()
        # print(jsonResponse)
        return jsonResponse

    async def get_string(self):
        listToStr = ', '.join([str(elem) for elem in self.titles])
        return listToStr

    async def create_task(self, title: str ):
        headers = {
            'Authorization': self.token,
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28',

        }

        url = 'https://api.notion.com/v1/pages'

        data = {"parent": {"database_id": self.data_base_id},
                "properties": {
                    "Name": {
                        "title": [
                            {
                                "text": {
                                    "content": title
                                }
                            }
                        ]

                    },
                    "Status": {
                        "select":
                            {
                                "name": "To Do"
                            }

                    }
                }
                }

        data = str(data)
        data = data.replace("'", '"')
        response = requests.post(url, headers=headers, data=data)
        jsonResponse = response.json()
        # print("create age response")
        # print(jsonResponse)
        return







