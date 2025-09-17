import json
import os
import re

import requests
from typing import List
from Entity import Song


class SearchEngine:
    """
    QQ音乐搜索和下载引擎
    支持搜索多首歌曲并提供下载功能
    """

    def __init__(self):
        try:
            with open('../../config/search_api.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.url = data['url']
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            raise Exception(f"配置文件 search_api.json 加载失败: {e}")

    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名中的非法字符，使其符合操作系统要求。
        """
        invalid_chars = r'[\\/:*?"<>|]'
        sanitized = re.sub(invalid_chars, '', filename)
        return sanitized.strip()

    def _fetch_data(self, endpoint: str, params: dict = None):
        """
        通用数据请求方法
        """
        try:
            response = requests.get(self.url + endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求失败: {e}")
        except json.JSONDecodeError:
            raise Exception("响应数据解析失败")

    def _select_songs(self, song_list: List[Song]) -> List[Song]:
        """
        让用户选择要下载的歌曲
        """
        if not song_list:
            print("没有找到任何歌曲。")
            return []

        print("\n请选择要下载的歌曲序号（多首请用逗号或空格分隔，如：1,3 5）：")
        for i, song in enumerate(song_list, 1):
            print(f"{i}. {song.title} - {song.artist}")

        while True:
            choice = input("请输入你的选择：")
            try:
                # 匹配由数字和逗号、空格组成的字符串
                indices = re.findall(r'\d+', choice)
                if not indices:
                    raise ValueError

                selected_indices = [int(idx) for idx in indices]

                selected_songs = []
                for idx in selected_indices:
                    if 1 <= idx <= len(song_list):
                        selected_songs.append(song_list[idx - 1])
                    else:
                        print(f"警告：序号 {idx} 不在有效范围内，已忽略。")

                if not selected_songs:
                    print("没有选择任何有效歌曲，请重新输入。")
                    continue

                return selected_songs

            except ValueError:
                print("输入格式错误，请重新输入有效的序号。")

    def search_all(self, keyword: str, limit: int = 10) -> List[Song]:
        """
        搜索所有匹配的歌曲信息
        """
        print(f"开始搜索: {keyword} {limit}首歌曲")
        search_result = self._fetch_data(endpoint='', params={'word': keyword})

        song_list = []
        for song_data in search_result.get('data', [])[:limit]:
            new_song = Song(song_data['id'], song_data['song'], song_data['singer'])
            song_list.append(new_song)

        print(f"搜索成功: {keyword} 共{len(song_list)}首歌曲")
        return song_list

    def download(self, song_list: List[Song], save_path: str = '../../downloads'):
        """
        下载歌曲列表中的所有歌曲
        """
        # 让用户选择要下载的歌曲
        selected_songs = self._select_songs(song_list)

        if not selected_songs:
            print("已取消下载。")
            return

        print(f"\n[*]开始下载选中的{len(selected_songs)}首歌曲")
        os.makedirs(save_path, exist_ok=True)

        for song in selected_songs:
            try:
                # 获取下载链接
                url_data = self._fetch_data(endpoint='', params={'id': song.id})
                song.url = url_data['data']['url']

                # 下载歌曲
                response = requests.get(song.url, stream=True, timeout=30)
                response.raise_for_status()

                sanitized_title = self._sanitize_filename(song.title)
                sanitized_artist = self._sanitize_filename(song.artist)
                file_path = os.path.join(save_path, f"{sanitized_title} - {sanitized_artist}.flac")

                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"下载成功: {song.title} - {song.artist}.flac")

            except Exception as e:
                print(f"下载 {song.title} - {song.artist} 失败: {e}")

        print("\n[*]下载完成")


# 使用示例
if __name__ == "__main__":
    sh = SearchEngine()
    # 搜索所有相关歌曲
    all_songs = sh.search_all('半岛铁盒', limit=5)
    # 调用 download 方法，它会先让用户选择再进行下载
    sh.download(all_songs)

    #命令行输入会阻塞，导致ui界面卡死