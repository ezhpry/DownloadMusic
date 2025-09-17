import json
import requests
import os
import re
from typing import List, Optional, Callable

def printa(data):
    print("数据：", data)
    print("类型：", type(data))



class SearchEngine:
    """
    QQ音乐搜索和下载引擎
    支持搜索多首歌曲并提供下载功能
    """
    def __init__(self):
        try:
            with open('config/search_api.json', 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            self.url = self.data['url']
        except FileNotFoundError:
            raise Exception("配置文件 search_api.json 不存在")
        except json.JSONDecodeError:
            raise Exception("配置文件 search_api.json 格式错误")
        except KeyError:
            raise Exception("配置文件中缺少必要的 url 字段")

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

    def get_first_songId(self, search_result: dict) -> str:
        """
        获取第一首歌曲的ID
        :param search_result: 搜索结果
        :return: 歌曲ID
        """
        try:
            if not search_result.get('data') or len(search_result['data']) == 0:
                raise Exception("搜索结果为空")
            return search_result['data'][0]['id']
        except (KeyError, IndexError):
            raise Exception("搜索结果格式异常")

    def get_all_songIds(self, search_result: dict) -> List[str]:
        """
        获取所有搜索到的歌曲ID列表
        :param search_result: 搜索结果
        :return: 歌曲ID列表
        """
        try:
            if not search_result.get('data'):
                return []
            return [song['id'] for song in search_result['data'] if 'id' in song]
        except (KeyError, TypeError):
            raise Exception("搜索结果格式异常")

    def search_song_byId(self, song_id: str) -> dict:
        """
        根据歌曲ID获取详细信息
        :param song_id: 歌曲ID
        :return: 歌曲详细信息
        """
        try:
            url = self.url + '?id=' + str(song_id)
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            resp = response.json()

            if not resp.get('data'):
                raise Exception("获取歌曲信息失败")

            return {
                'id': song_id,
                'song': resp['data'].get('song', '未知歌曲'),
                'singer': resp['data'].get('singer', '未知歌手'),
                'url': resp['data'].get('url', '')
            }
        except requests.exceptions.RequestException as e:
            raise Exception(f"获取歌曲信息请求失败: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("歌曲信息解析失败")


    def search(self, data: str, mode: str = 'k') -> Optional[dict]:
        """
        核心搜索功能 - 返回第一首歌曲
        :param data: 搜索关键词
        :param mode: 搜索模式，默认为'k'，即搜索关键字（歌曲名字，歌手名字）
        :return: 第一首歌曲信息或None
        """
        if mode == 'k':
            search_result = self.search_by_word(data)
            song_id = self.get_first_songId(search_result)
            song_info = self.search_song_byId(song_id)
            return song_info
        return None

    def search_all(self, keyword: str, limit: int = 10) -> List[dict]:
        """
        搜索所有匹配的歌曲信息
        :param keyword: 搜索关键词
        :param limit: 返回结果数量限制，默认10首
        :return: 歌曲信息列表
        """
        try:
            # 获取搜索结果
            search_result = self.search_by_word(keyword)
            song_ids = self.get_all_songIds(search_result)

            if not song_ids:
                return []

            # 限制返回数量
            song_ids = song_ids[:limit]

            # 获取每首歌曲的详细信息
            songs_info = []
            for song_id in song_ids:
                try:
                    song_info = self.search_song_byId(song_id)
                    songs_info.append(song_info)
                except Exception as e:
                    print(f"获取歌曲 {song_id} 信息失败: {str(e)}")
                    continue

            return songs_info

        except Exception as e:
            print(f"搜索失败: {str(e)}")
            return []

    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名，移除非法字符
        :param filename: 原始文件名
        :return: 清理后的文件名
        """
        # 移除或替换非法字符
        illegal_chars = r'[<>:"/\\|?*]'
        filename = re.sub(illegal_chars, '_', filename)
        # 移除首尾空格和点号
        filename = filename.strip('. ')
        # 限制长度
        return filename[:100] if len(filename) > 100 else filename

    def download(self, song_info: dict, save_path: str = './downloads',
                progress_callback: Optional[Callable[[int, int], None]] = None) -> str:
        """
        下载歌曲
        :param song_info: 歌曲信息字典
        :param save_path: 保存路径
        :param progress_callback: 进度回调函数 callback(downloaded, total)
        :return: 下载的文件路径
        """
        song_name = song_info.get('song', '未知歌曲')
        song_singer = song_info.get('singer', '未知歌手')
        song_url = song_info.get('url', '')

        if not song_url:
            raise Exception("歌曲下载链接无效")

        # 清理文件名
        safe_song_name = self._sanitize_filename(song_name)
        safe_singer_name = self._sanitize_filename(song_singer)
        filename = f"{safe_song_name}-{safe_singer_name}.flac"

        # 确保保存目录存在
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        file_path = os.path.join(save_path, filename)

        try:
            response = requests.get(song_url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)

                        # 调用进度回调
                        if progress_callback:
                            progress_callback(downloaded_size, total_size)

            print(f'[*]下载成功: {song_name} - {song_singer}.flac')
            return file_path

        except requests.exceptions.RequestException as e:
            if os.path.exists(file_path):
                os.remove(file_path)  # 删除不完整的文件
            raise Exception(f"下载失败: {str(e)}")
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise Exception(f"保存文件失败: {str(e)}")

# 使用示例
if __name__ == "__main__":
    sh = SearchEngine()

    # # 搜索第一首歌曲
    # song_info = sh.search('半岛铁盒')
    # if song_info:
    #     print(f"找到歌曲: {song_info['song']} - {song_info['singer']}")
    #     # sh.download(song_info, save_path='./')

    # 搜索所有相关歌曲
    all_songs = sh.search_all('美瞳', limit=5)
    print(f"\n找到 {len(all_songs)} 首相关歌曲:")
    for i, song in enumerate(all_songs, 1):
        print(f"{i}. {song['song']} - {song['singer']}")
        sh.download(song, save_path='./')

