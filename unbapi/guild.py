import requests
from typing import Union, Optional, Literal, TypeVar, Iterable, TYPE_CHECKING

from .exceptions import InvalidToken, NotFound, Forbidden, unbapiException
from .user import PartialUser, User
from .items import Item

if TYPE_CHECKING:
    from .application import Application

__all__ = (
    "GuildPermissions",
    "PartialGuild",
    "Guild"
)

class GuildPermissions():
    def __init__(self, bitwise) -> None:
        self.economy: bool = bool(bitwise & 1 << 0)
        self.items: bool = bool(bitwise & 1 << 1)
        self.bitwise: int = bitwise
    
    def __repr__(self) -> str:
        return f"unbapi.GuildPermissions(economy={self.economy}, items={self.items})"

class PartialGuild():
    def __init__(self, id: int, application: "Application", token: str):
        self.id: int = id
        self.application: Application = application
        self.leaderboard_url: str = f"https://unbelievaboat.com/leaderboard/{self.id}"
        self.__token = token
    
    def __repr__(self) -> str:
        return f"unbapi.PartialGuild(id={self.id})"

    def fetch_permissions(self) -> GuildPermissions:
        """
        Fetches the permissions the application has in the guild. Returns a `GuildPermissions` object with `economy`, and `items` attributes.
        """

        response = requests.get(f"https://unbelievaboat.com/api/v1/applications/@me/guilds/{self.id}", headers={
            "authorization": self.__token
        })

        if response.status_code == 401: raise InvalidToken(response.json().get("message", "Token is not valid"))
        if response.status_code == 403: raise Forbidden(response.json().get("message", "This App is not allowed to access this resource"))
        if response.status_code == 404: raise NotFound(response.json().get("message", "Unkown Guild"))
        elif not response.ok: raise unbapiException(response.json().get("message", "HTTP request failed."))

        return GuildPermissions(response.json()["permissions"])
    
    def get_user(self, user_id: Union[int, str, TypeVar("ObjectWithIdAttribute")]) -> PartialUser:
        """
        Creates a partial user object. Useful if you don't need the current balance/rank, but need to change the balance or inventory.

        :param user_id: The user id either as an int, str, or an object with an `id` attribute (such as discord.py's User object).
        """

        if type(user_id) == str:
            user_id = int(user_id)
        elif not type(user_id) == int:
            try:
                user_id = user_id.id
            except(AttributeError):
                raise TypeError("user_id object doesn't have an id attribute.")
            
        return PartialUser(user_id, self, self.__token)
    
    def fetch_user(self, user_id: Union[int, str, TypeVar("ObjectWithIdAttribute")]) -> User:
        """
        Fetches the user's balance, and returns a `User` object.

        :param user_id: The user id either as an int, str, or an object with an `id` attribute (such as discord.py's User object).
        """

        if type(user_id) == str:
            user_id = int(user_id)
        elif not type(user_id) == int:
            try:
                user_id = user_id.id
            except(AttributeError):
                raise TypeError("user_id object doesn't have an id attribute.")

        response = requests.get(f"https://unbelievaboat.com/api/v1/guilds/{self.id}/users/{user_id}", headers={
            "authorization": self.__token
        })

        if response.status_code == 401: raise InvalidToken(response.json().get("message", "Token is not valid"))
        if response.status_code == 403: raise Forbidden(response.json().get("message", "This App is not allowed to access this resource"))
        if response.status_code == 404: raise NotFound(response.json().get("message", "Unkown Guild"))
        elif not response.ok: raise unbapiException(response.json().get("message", "HTTP request failed."))

        return User(user_id, self, self.__token, response.json())

    def fetch_leaderboard(self, sort: Literal["cash", "bank", "total"] = "total", limit: Optional[int]=None) -> Iterable[User]:
        """
        Iterates throught every user on the guild's leaderboard, from highest to lower.

        ```py
        for user in guild.fetch_leaderboard():
            print(user.id, user.rank, user.total)
        ```

        It can be converted to a list using:
        ```py
        list(guild.fetch_leaderboard())
        ```

        :param sort: What order the users should be returned in. Allowed values are: `cash`, `bank`, and `total`
        :param limit: The maximum number of users to yield
        """

        page = 1
        yields = 0
        while limit == None or yields < limit:
            response = requests.get(f"https://unbelievaboat.com/api/v1/guilds/{self.id}/users", headers={
                "authorization": self.__token
            }, params={
                "limit": limit - yields if limit and limit - yields < 1000 else 1000,
                "sort": sort,
                "page": page
            })

            if response.status_code == 401: raise InvalidToken(response.json().get("message", "Token is not valid"))
            if response.status_code == 403: raise Forbidden(response.json().get("message", "This App is not allowed to access this resource"))
            if response.status_code == 404: raise NotFound(response.json().get("message", "Unkown Guild"))
            elif not response.ok: raise unbapiException(response.json().get("message", "HTTP request failed."))

            data = response.json()
            for user in data["users"]:
                yield User(int(user['user_id']), self, self.__token, user)

                yields += 1
                if limit != None and yields >= limit: break
            page += 1
            if page > data["total_pages"]: break
    
    def fetch_items(self, sort: Literal["id", "price", "name", "stock_remaining", "expires_at"] = "id", limit: Optional[int]=None) -> Iterable[Item]:
        """
        Iterates throught every item in the guild's store.

        ```py
        for item in guild.fetch_items():
            print(item.id, item.name, item.price)
        ```

        It can be converted to a list using:
        ```py
        list(guild.fetch_items())
        ```

        :param sort: What order the items should be returned in. Allowed values are: `id`, `price`, `name`, `stock_remaining`, and `expires_at`
        :param limit: The maximum number of items to yield
        """

        page = 1
        yields = 0
        while limit == None or yields < limit:
            response = requests.get(f"https://unbelievaboat.com/api/v1/guilds/{self.id}/items", headers={
                "authorization": self.__token
            }, params={
                "limit": limit - yields if limit and limit - yields < 1000 else 1000,
                "sort": sort,
                "page": page
            })

            if response.status_code == 401: raise InvalidToken(response.json().get("message", "Token is not valid"))
            if response.status_code == 403: raise Forbidden(response.json().get("message", "This App is not allowed to access this resource"))
            if response.status_code == 404: raise NotFound(response.json().get("message", "Unkown Guild"))
            elif not response.ok: raise unbapiException(response.json().get("message", "HTTP request failed."))

            data = response.json()
            for item in data["items"]:
                yield Item(int(item['id']), self, self.__token, item)

                yields += 1
                if limit != None and yields >= limit: break
            page += 1
            if page > data["total_pages"]: break
    
    def fetch_item(self, item_id: Union[int, str, TypeVar("ObjectWithIdAttribute")]) -> Item:
        """
        Fetches the information about an item.

        :param item_id: The item id either as an int, str, or an object with an `id` attribute.
        """

        if type(item_id) == str:
            item_id = int(item_id)
        elif not type(item_id) == int:
            try:
                item_id = item_id.id
            except(AttributeError):
                raise TypeError("item_id object doesn't have an id attribute.")

        response = requests.get(f"https://unbelievaboat.com/api/v1/guilds/{self.id}/items/{item_id}", headers={
            "authorization": self.__token
        })

        if response.status_code == 401: raise InvalidToken(response.json().get("message", "Token is not valid"))
        if response.status_code == 403: raise Forbidden(response.json().get("message", "This App is not allowed to access this resource"))
        if response.status_code == 404: raise NotFound(response.json().get("message", "Unkown Guild"))
        elif not response.ok: raise unbapiException(response.json().get("message", "HTTP request failed."))

        return Item(item_id if type(item_id) == int else int(item_id), self, self.__token, response.json())

class Guild(PartialGuild):
    def __init__(self, guild_id: int, application: "Application", token: str, data: dict):
        super().__init__(guild_id, application, token)
        self.name: str = data["name"]
        self.icon: str = data['icon']
        self.icon_url: str = f"https://cdn.discordapp.com/icons/{guild_id}/{data['icon']}{'.png' if not data['icon'].startswith('a_') else '.gif'}" if data['icon'] else None
        self.member_count: int = data["member_count"]
        self.owner_id: PartialUser = PartialUser(data["owner_id"], self, token)
        self.symbol: str = data["symbol"]
        self.premium: bool = data["premium"]
        self.vanity_code: str = data["vanity_code"]
        if self.vanity_code: self.leaderboard_url: str = f"https://unbelievaboat.com/leaderboard/{self.vanity_code}"
        self.__token = token
    
    def __repr__(self) -> str:
        return f"unbapi.Guild(id={self.id}, name=\"{self.name}\")"