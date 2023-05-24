import requests
from typing import Union, Optional, Literal, Iterable, TYPE_CHECKING, TypeVar
import math

from .exceptions import InvalidToken, NotFound, Forbidden, unbapiException
from .items import Item

if TYPE_CHECKING:
    from .guild import PartialGuild, Guild

__all__ = (
    "PartialUser",
    "User"
)

class PartialUser():
    def __init__(self, id: int, guild: Union["PartialGuild", "Guild"], token: str):
        self.id: int = id
        self.guild: Union[PartialGuild, Guild] = guild
        self.__token = token
    
    def __repr__(self) -> str:
        return f"unbapi.PartialUser(id={self.id})"
    
    def update_balance(self, cash: Optional[Union[int, "math.inf"]]=0, bank: Optional[Union[int, "math.inf"]]=0, reason: Optional[str]=None):
        """
        Changes the user's balance by the number provided, use negative numbers to remove money. Returns a `user` object **without** the `rank`.
        
        For example bank=300 would add 300 money to their bank balance, while cash=-200 will remove 200 money from their cash.

        :param cash: The amount to change their cash balance.
        :param bank: The amount to change their bank balance.
        :param reason: The reason to appear in the economy logs.
        """

        response = requests.patch(f"https://unbelievaboat.com/api/v1/guilds/{self.guild.id}/users/{self.id}", headers={
            "authorization": self.__token
        }, json={
            "cash": cash if not cash == math.inf else "Infinity",
            "bank": bank if not bank == math.inf else "Infinity",
            "reason": reason
        })

        if response.status_code == 401: raise InvalidToken(response.json().get("message", "Token is not valid"))
        if response.status_code == 403: raise Forbidden(response.json().get("message", "This App is not allowed to access this resource"))
        if response.status_code == 404: raise NotFound(response.json().get("message", "Unkown Guild"))
        elif not response.ok: raise unbapiException(response.json().get("message", "HTTP request failed."))

        return User(self.id, self.guild, self.__token, response.json())

    def set_balance(self, cash: Optional[Union[int, "math.inf"]]=0, bank: Optional[Union[int, "math.inf"]]=0, reason: Optional[str]=None):
        """
        Sets the user's balance to the number(s) provided. Returns a `user` object **without** the `rank`.
        
        For example bank=300 would set their bank balance to 300, while cash=math.inf will set their cash to infinity.

        :param cash: The amount to set their cash balance.
        :param bank: The amount to set their bank balance.
        :param reason: The reason to appear in the economy logs.
        """

        response = requests.put(f"https://unbelievaboat.com/api/v1/guilds/{self.guild.id}/users/{self.id}", headers={
            "authorization": self.__token
        }, json={
            "cash": cash if not cash == math.inf else "Infinity",
            "bank": bank if not bank == math.inf else "Infinity",
            "reason": reason
        })

        if response.status_code == 401: raise InvalidToken(response.json().get("message", "Token is not valid"))
        if response.status_code == 403: raise Forbidden(response.json().get("message", "This App is not allowed to access this resource"))
        if response.status_code == 404: raise NotFound(response.json().get("message", "Unkown Guild"))
        elif not response.ok: raise unbapiException(response.json().get("message", "HTTP request failed."))

        return User(self.id, self.guild, self.__token, response.json())

    def fetch_inventory(self, sort: Literal["item_id", "name", "quantity"] = "item_id", limit: Optional[int]=None) -> Iterable[Item]:
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
            response = requests.get(f"https://unbelievaboat.com/api/v1/guilds/{self.guild.id}/users/{self.id}/inventory", headers={
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
                yield Item(int(item['item_id']), self, self.__token, item)

                yields += 1
                if limit != None and yields >= limit: break
            page += 1
            if page > data["total_pages"]: break
    
    def fetch_item_quantity(self, item_id: Union[int, str, Item, TypeVar("ObjectWithIdAttribute")]) -> int:
        """
        Returns the quantity of the item the user has. 0 if they don't have any.

        :param item_id: The ID of the item to check for.
        """

        if type(item_id) == str:
            item_id = int(item_id)
        elif not type(item_id) == int:
            try:
                item_id = item_id.id
            except(AttributeError):
                raise TypeError("item_id object doesn't have an id attribute.")

        response = requests.get(f"https://unbelievaboat.com/api/v1/guilds/{self.guild.id}/users/{self.id}/inventory/{item_id}", headers={
            "authorization": self.__token
        })

        if response.status_code == 404 and response.json().get("message") == "Unknown item":
            return 0

        if response.status_code == 401: raise InvalidToken(response.json().get("message", "Token is not valid"))
        if response.status_code == 403: raise Forbidden(response.json().get("message", "This App is not allowed to access this resource"))
        if response.status_code == 404: raise NotFound(response.json().get("message", "Unkown Guild"))
        elif not response.ok: raise unbapiException(response.json().get("message", "HTTP request failed."))

        return int(response.json()["quantity"])

    def add_item(self, item_id: Union[int, str, Item, TypeVar("ObjectWithIdAttribute")], quantity: Optional[int]=1, origin_inventory_user_id: Optional[int]=None) -> Item:
        """
        Adds an item to the user's inventory.

        :param item_id: The ID of the item to add to the user's inventory.
        :param quantity: The number of the item to add to the user's inventory.
        :param origin_inventory_user_id: If the item is no longer for sale, an ID of the inventory to copy it from.
        """

        if type(item_id) == str:
            item_id = int(item_id)
        elif not type(item_id) == int:
            try:
                item_id = item_id.id
            except(AttributeError):
                raise TypeError("item_id object doesn't have an id attribute.")

        response = requests.post(f"https://unbelievaboat.com/api/v1/guilds/{self.guild.id}/users/{self.id}/inventory", headers={
            "authorization": self.__token
        }, json={
            "item_id": str(item_id),
            "quantity": quantity,
            "options": {
                "inventory_user_id": origin_inventory_user_id
            }
        })

        if response.status_code == 401: raise InvalidToken(response.json().get("message", "Token is not valid"))
        if response.status_code == 403: raise Forbidden(response.json().get("message", "This App is not allowed to access this resource"))
        if response.status_code == 404: raise NotFound(response.json().get("message", "Unkown Guild"))
        elif not response.ok: raise unbapiException(response.json().get("message", "HTTP request failed."))

        return Item(item_id if type(item_id) == int else int(item_id), self, self.__token, response.json())
    
    def remove_item(self, item_id: Union[int, str, Item, TypeVar("ObjectWithIdAttribute")], quantity: Optional[int]=1) -> None:
        """
        Removes an item to the user's inventory.

        :param item_id: The ID of the item to add to the user's inventory.
        :param quantity: The number of the item to add to the user's inventory.
        :param origin_inventory_user_id: If the item is no longer for sale, an ID of the inventory to copy it from.
        """

        if type(item_id) == str:
            item_id = int(item_id)
        elif not type(item_id) == int:
            try:
                item_id = item_id.id
            except(AttributeError):
                raise TypeError("item_id object doesn't have an id attribute.")

        response = requests.delete(f"https://unbelievaboat.com/api/v1/guilds/{self.guild.id}/users/{self.id}/inventory/{item_id}", headers={
            "authorization": self.__token
        }, params={
            "quantity": quantity
        })

        if response.status_code == 401: raise InvalidToken(response.json().get("message", "Token is not valid"))
        if response.status_code == 403: raise Forbidden(response.json().get("message", "This App is not allowed to access this resource"))
        if response.status_code == 404: raise NotFound(response.json().get("message", "Unkown Guild"))
        elif not response.ok: raise unbapiException(response.json().get("message", "HTTP request failed."))

class User(PartialUser):
    def __init__(self, id: int, guild: Union["PartialGuild", "Guild"], token: str, data: dict):
        super().__init__(id, guild, token)
        self.rank: Optional[int] = int(data["rank"]) if data.get("rank") else None

        self.cash: Union[int, "math.inf"] = data["cash"] if not data["cash"] == "Infinity" else math.inf
        self.bank: Union[int, "math.inf"] = data["bank"] if not data["bank"] == "Infinity" else math.inf
        self.total: Union[int, "math.inf"] = data["total"] if not data["total"] == "Infinity" else math.inf
    
    def __repr__(self) -> str:
        return f"unbapi.User(id={self.id}, cash={self.cash}, bank={self.bank})"