import json

import requests

def printa(data):
    print("数据：", data)
    print("类型：", type(data))



class SearchEngine:
    """
    Download songs from QQMusic
    """
    def __init__(self):
        self.data=json.loads(open('search_api.json', 'r', encoding='utf-8').read())
        self.url=self.data['url']

    def search_by_word(self,keyword)->dict:
        url = self.url + '?word=' + keyword
        response = requests.get(url)
        return response.json()

    def get_first_songId(self,search_result:dict)->str:
        return search_result['data'][0]['id']

    def search_song_byId(self,id):
        url = self.url + '?id=' + str(id)
        response = requests.get(url)
        resp=response.json()
        return {
            'song':resp['data']['song'],
            'singer':resp['data']['singer'],
            'url':resp['data']['url']
        }


    def search(self,data,mode='k',):
        """
        核心搜索功能
        :param data:
        :param mode: 搜索模式，默认为‘k'，即搜索关键字（歌曲名字，歌手名字）
        :return:
        """
        if mode=='k':
            searchResult=self.search_by_word(data)
            songId=self.get_first_songId(searchResult)
            songInfo=self.search_song_byId(songId)
            return songInfo

    def download(self,songInfo:dict,save_path:str='./'):
        songName=songInfo['song']
        songSinger=songInfo['singer']
        songUrl=songInfo['url']
        response = requests.get(songUrl)
        with open(save_path+'/'+songName+'-'+songSinger+'.flac', 'wb') as f:
            f.write(response.content)
            print(f'[*]下载成功: {songName} - {songSinger}.flac')

sh=SearchEngine()

songInfo=sh.search('半岛铁盒')
sh.download(songInfo,save_path='./')

