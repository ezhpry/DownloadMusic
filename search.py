import json

import requests

class SearchEngine:
    """
    Download songs from QQMusic
    """
    def __init__(self):
        self.data=json.loads(open('search_api.json', 'r', encoding='utf-8').read())
        self.url=self.data['url']

    def search_by_input_word(self):
        keyword=input("请输入搜索关键词：")
        url = self.url + '?word=' + keyword
        response = requests.get(url)
        return response.json()


    def search_by_word(self,keyword):
        url = self.url + '?word=' + keyword
        response = requests.get(url)
        return response.json()

    def search_by_id(self, id):
        url = self.url + '?id=' + str(id)
        response = requests.get(url)
        return response.json()

    def get_song_firstId(self,search_result)->str:
        firstId=search_result['data']['id']
        return firstId

sh=SearchEngine()

info=sh.search_by_word('lemon tree')
