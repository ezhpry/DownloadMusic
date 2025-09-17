# Entity.py
class Song:
    def __init__(self, id, title, artist):
        self.id = id
        self.title = title
        self.artist = artist
        self.url = None
    def __repr__(self):
        return f"Song(id={self.id}, title='{self.title}', artist='{self.artist} url={self.url}')"