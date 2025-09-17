import json
import os

import requests
from typing import List
from Entity import Song


def printa(data):
    print("数据：", data)
    print("类型：", type(data))

import re



class SearchEngine:
    """
    QQ音乐搜索和下载引擎
    支持搜索多首歌曲并提供下载功能
    """
    def __init__(self):

        try:
            with open('../../config/search_api.json', 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            self.url = self.data['url']
        except FileNotFoundError:
            raise Exception("配置文件 search_api.json 不存在")
        except json.JSONDecodeError:
            raise Exception("配置文件 search_api.json 格式错误")
        except KeyError:
            raise Exception("配置文件中缺少必要的 url 字段")

    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名中的非法字符，使其符合操作系统要求。
        """
        # 匹配所有不安全的字符，并替换为空格或空字符串
        # 常见的非法字符：\ / : * ? " < > |
        invalid_chars = r'[\\/:*?"<>|]'
        sanitized = re.sub(invalid_chars, '', filename)
        return sanitized.strip()

    def search_by_word(self, keyword: str) -> dict:
        """
        根据关键词搜索歌曲
        :param keyword: 搜索关键词
        :return: 搜索结果字典
        """
        try:
            url = self.url + '?word=' + keyword
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # 检查HTTP错误
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"搜索请求失败: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("搜索结果解析失败")




    def search_all(self, keyword: str, limit: int = 10) -> List[Song]:
        """
        搜索所有匹配的歌曲信息
        :param keyword: 搜索关键词
        :param limit: 返回结果数量限制，默认10首
        :return: 歌曲信息列表
        """
        try:
            print(f"开始搜索: {keyword} {limit}首歌曲")
            # 获取搜索结果
            search_result = self.search_by_word(keyword)
            # 歌曲资源列表
            songSourceList=search_result['data']
            print(f'[*]成功获得歌曲资源列表')
            # 歌曲数量
            songList=[]
            count=0
            for song in songSourceList:
                if count>=limit:
                    break
                count+=1
                newSong=Song(song['id'],song['song'],song['singer'])
                songList.append(newSong)
            print(f"搜索成功: {keyword} 共{len(songList)}首歌曲")
            return songList


        except Exception as e:
            print(f"搜索失败: {str(e)}")
            return []

    def get_url_by_id(self,id:str):
        response=requests.get(self.url+'?id='+str(id))
        response.raise_for_status()
        data=response.json()
        return data['data']['url']


    def download_song(self,song:Song,save_path='../../downloads'):
        if song.url:
            response=requests.get(song.url)
            response.raise_for_status()
            sanitized_title = self._sanitize_filename(song.title)
            sanitized_artist = self._sanitize_filename(song.artist)
            file_path = save_path + '/' + sanitized_title + '-' + sanitized_artist + '.flac'

            # 确保保存目录存在
            os.makedirs(save_path, exist_ok=True)


            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"下载成功: {song.title} - {song.artist}.flac")




    def downloadAll(self,songList:list[Song],save_path='../../downloads'):
        for song in songList:
            song.url=self.get_url_by_id(song.id)
            self.download_song(song, save_path)
        print(f"[*]下载完成 共{len(songList)}首歌曲")



    def download(self,songList:list[Song],save_path='../../downloads',all=False):
        pass




# 使用示例
if __name__ == "__main__":
    sh = SearchEngine()
    # 搜索所有相关歌曲
    all_songs = sh.search_all('美瞳', limit=5)
    sh.downloadAll(all_songs)


