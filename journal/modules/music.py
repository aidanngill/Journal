from typing import List
from datetime import datetime

from ..format import Line
from ..session import Session


class LastFm(Line):
    def __init__(self, category, **kwargs):
        super().__init__(
            category, "Last.fm", "https://last.fm/", "https://last.fm/user/"
        )

        # No processing necessary.
        self.url = kwargs.get("url", None)

        # Title can be `title` or `name`.
        title = kwargs.get("title", None)

        if title is None:
            title = kwargs.get("name", None)

        self.title = title

        # Make sure plays are a number.
        self.playcount = int(kwargs.get("playcount", 0))

        # Get basic artist information.
        artist = kwargs.get("artist", None)
        self.artist = None

        if artist is not None:
            self.artist = Artist(**artist)

        # Choose the highest quality if we're given a dictionary of images.
        images = kwargs.get("image", None)
        self.image = None

        if images is not None:
            if isinstance(images, dict):
                self.image = images[-1].get("#text", None)
            elif isinstance(images, str):
                self.image = images

    @classmethod
    def from_last_fm(cls, data: dict):
        return cls(
            artist=data.get("artist"),
            title=data.get("name"),
            url=data.get("url"),
            image=data.get("image"),
            playcount=data.get("playcount"),
        )


class Artist(LastFm):
    def __init__(self, **kwargs):
        super().__init__("Artist", **kwargs)

    def make_line(self):
        return f"* {self.title}[{self.url}]"


class Album(LastFm):
    def __init__(self, **kwargs):
        super().__init__("Album", **kwargs)

    def make_line(self):
        return (
            f"* ({self.artist.title})[{self.artist.url}] - ({self.title})[{self.url}]"
        )


class Track(LastFm):
    def __init__(self, **kwargs):
        super().__init__("Track", **kwargs)

    def make_line(self):
        return (
            f"* ({self.artist.title})[{self.artist.url}] - ({self.title})[{self.url}]"
        )


class Profile(LastFm):
    def __init__(self, **kwargs):
        super().__init__("Profile", **kwargs)

        self.realname = kwargs.get("realname", "")
        self.country = kwargs.get("country", "")
        self.name = kwargs.get("name")

        # Requires processing.
        self.registered = datetime.fromtimestamp(kwargs["registered"]["#text"])

    @classmethod
    def from_last_fm(cls, data: dict):
        return cls(**data)

    def category_multiple(self):
        return self.category

    def make_block(self):
        lines = [
            f"__{self.category_multiple()}__",
            f"Name: ({self.name})[{self.url}] ({self.realname})",
            f"Registered: {self.registered.strftime('%b %e %Y at %H:%M')}",
            f"Plays: {self.playcount}",
            f"Location: {self.country}",
        ]

        return "\n* ".join(lines)


class AudioScrobbler(Session):
    functions = ("profile_info", "top_albums", "top_artists", "top_tracks")

    def __init__(self):
        super().__init__(
            "https://ws.audioscrobbler.com/2.0/",
            is_json=True,
            default_params={"format": "json"},
        )

    def set_authorization(self, authorization):
        self.default_params["api_key"] = authorization

    def profile_info(self, user: str):
        params = {"method": "user.getInfo", "user": user}

        return Profile.from_last_fm(self.fetch(params=params).get("user", {}))

    def top_albums(self, user, period="7day", limit=5, page=1):
        params = {
            "method": "user.getTopAlbums",
            "user": user,
            "period": period,
            "limit": limit,
            "page": page,
        }

        return [
            Album.from_last_fm(album)
            for album in self.fetch(params=params).get("topalbums", {}).get("album", [])
        ]

    def top_artists(self, user, period="7day", limit=5, page=1):
        params = {
            "method": "user.getTopArtists",
            "user": user,
            "period": period,
            "limit": limit,
            "page": page,
        }

        return [
            Artist.from_last_fm(artist)
            for artist in self.fetch(params=params)
            .get("topartists", {})
            .get("artist", [])
        ]

    def top_tracks(self, user, period="7day", limit=5, page=1):
        params = {
            "method": "user.getTopTracks",
            "user": user,
            "period": period,
            "limit": limit,
            "page": page,
        }

        return [
            Track.from_last_fm(track)
            for track in self.fetch(params=params).get("toptracks", {}).get("track", [])
        ]
