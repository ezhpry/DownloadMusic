import flet as ft
from search import SearchEngine, Song

def main(page: ft.Page):
    page.title = "QQ音乐搜索下载器"
    page.scroll = "auto"
    page.theme_mode = "light"

    engine = SearchEngine()

    # 输入框
    keyword_input = ft.TextField(label="请输入歌曲关键词", width=400)
    limit_input = ft.TextField(label="搜索数量", value="10", width=100)

    # 搜索结果显示
    song_list_view = ft.ListView(expand=True, spacing=5, padding=5)
    songs: list[Song] = []
    checkboxes: list[ft.Checkbox] = []

    # 搜索函数
    def search_songs(e):
        song_list_view.controls.clear()
        checkboxes.clear()

        keyword = keyword_input.value.strip()
        if not keyword:
            page.snack_bar = ft.SnackBar(ft.Text("请输入搜索关键词！"), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        try:
            limit = int(limit_input.value.strip() or "10")
        except ValueError:
            limit = 10

        try:
            nonlocal songs
            songs = engine.search_all(keyword, limit=limit)

            if not songs:
                song_list_view.controls.append(ft.Text("没有找到相关歌曲", color="red"))
            else:
                for idx, song in enumerate(songs, 1):
                    cb = ft.Checkbox(label=f"{idx}. {song.title} - {song.artist}")
                    checkboxes.append(cb)
                    song_list_view.controls.append(cb)

            page.update()

        except Exception as ex:
            song_list_view.controls.append(ft.Text(f"搜索失败: {ex}", color="red"))
            page.update()

    # 下载函数
    def download_selected(e):
        selected = [songs[i] for i, cb in enumerate(checkboxes) if cb.value]
        if not selected:
            page.snack_bar = ft.SnackBar(ft.Text("请先选择要下载的歌曲"), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        # 异步下载提示
        page.snack_bar = ft.SnackBar(ft.Text(f"开始下载 {len(selected)} 首歌曲..."), bgcolor="blue")
        page.snack_bar.open = True
        page.update()

        engine.download(selected)

        page.snack_bar = ft.SnackBar(ft.Text("下载完成！"), bgcolor="green")
        page.snack_bar.open = True
        page.update()

    # 控件和布局
    search_button = ft.ElevatedButton("搜索", on_click=search_songs, bgcolor="blue", color="white")
    download_button = ft.ElevatedButton("下载选中歌曲", on_click=download_selected, bgcolor="green", color="white")

    page.add(
        ft.Column(
            [
                ft.Row([keyword_input, limit_input, search_button], spacing=10),
                ft.Container(download_button, padding=5),
                ft.Container(song_list_view, expand=True, width=600, height=400, border=ft.border.all(1, "gray")),
            ],
            expand=True,
            spacing=10,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
