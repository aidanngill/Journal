from datetime import datetime

from ..format import Line
from ..session import Session


class Steam(Line):
    def __init__(self, category, **kwargs):
        super().__init__(
            category,
            "Steam",
            "https://steamcommunity.com/",
            "https://steamcommunity.com/profiles/",
        )


class Profile(Steam):
    def __init__(
        self,
        id: int,
        persona: str,
        registered: int,
        real_name: str = None,
        location: str = None,
        game_count: int = 0,
    ):
        super().__init__("Profile")

        self.id = id
        self.persona = persona

        self.registered = datetime.fromtimestamp(registered)

        # Optional parameters.
        self.real_name = real_name
        self.location = location
        self.game_count = game_count

    @classmethod
    def from_steam(cls, data):
        data = data["response"]["players"][0]

        return cls(
            id=int(data.get("steamid", 0)),
            persona=data.get("personaname", ""),
            registered=data.get("timecreated", 0),
            real_name=data.get("realname", ""),
            location=data.get("loccountrycode", ""),
        )

    def category_multiple(self):
        return self.category

    def make_block(self):
        lines = [
            f"__{self.category_multiple()}__",
            f"Name: {self.persona} ({self.real_name})",
            f"ID: ({self.id!r})[{self.profile_link(self.id)}]",
            f"Registered: {self.registered.strftime('%b %e %Y at %H:%M')}",
            f"Games: {self.game_count!r}",
            f"Location: {self.location.upper()}",
        ]

        return "\n* ".join(lines)


class Game(Steam):
    def __init__(self, id: int, title: str, recent: int = 0, total: int = 0):
        super().__init__("Game")

        self.id = id
        self.title = title

        self.recent = recent
        self.total = total

    @classmethod
    def from_steam(cls, data):
        return cls(
            id=data.get("appid", 0),
            title=data.get("name", ""),
            recent=data.get("playtime_2weeks", 0),
            total=data.get("playtime_forever", 0),
        )

    @property
    def url(self):
        return f"https://store.steampowered.com/app/{self.id!r}"

    def make_line(self):
        return (
            f"* ({self.title})[{self.url}] "
            f"({self.recent / 60:.1f} hours recently, "
            f"{self.total / 60:.1f} hours overall)"
        )


class Steam(Session):
    functions = ("recently_played", "profile_info")

    def __init__(self):
        super().__init__(
            "https://api.steampowered.com/",
            is_json=True,
            default_params={"format": "json"},
        )

    def set_authorization(self, authorization):
        self.default_params["key"] = authorization

    def get_game_count(self, user: int):
        return self.fetch(
            "GET", "IPlayerService/GetOwnedGames/v0001/", params={"steamid": user}
        )["response"].get("game_count", 0)

    def recently_played(self, user: int):
        return [
            Game.from_steam(game)
            for game in self.fetch(
                "GET",
                "IPlayerService/GetRecentlyPlayedGames/v0001/",
                params={"steamid": user},
            )["response"].get("games", [])
        ]

    def profile_info(self, user: int):
        item = Profile.from_steam(
            self.fetch(
                "GET", "ISteamUser/GetPlayerSummaries/v0002/", params={"steamids": user}
            )
        )

        item.game_count = self.get_game_count(user)

        return item
