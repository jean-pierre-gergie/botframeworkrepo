import json
import requests
import aiohttp
import asyncio

# key= 'd487497579da415e8c9da3d63cf86a70'
#
# email='jpgergie@gmail.com'
# response = requests.get\
#     ("https://emailvalidation.abstractapi.com/v1/?api_key=d487497579da415e8c9da3d63cf86a70&email="+email)
# print(response.status_code)
# print(response.content)

class EmailValidator:
    def __init__(self,email:str):
        self.email =email
    async def check_validity(self):
        response = requests.get \
                ("https://emailvalidation.abstractapi.com/v1/?api_key=d487497579da415e8c9da3d63cf86a70&email="+self.email)
        result = json.loads(response.content)

        if result['deliverability'] == 'DELIVERABLE':
            print("the email is  DELIVERABLE")
            return True
        else:
            return False



