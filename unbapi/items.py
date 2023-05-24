import requests
from typing import Union, Optional, TYPE_CHECKING
import math
from datetime import datetime
from enum import Enum

from .exceptions import InvalidToken, NotFound, Forbidden, unbapiException

if TYPE_CHECKING:
    from .guild import PartialGuild, Guild

class ItemRequirementType(Enum):
    ROLE = 1
    TOTAL_BALANCE = 2
    ITEM = 3

class ItemMatchType(Enum):
    ALL = 1
    ANY = 2
    NONE = 3

class ItemActionType(Enum):
    RESPOND	= 1
    ADD_ROLES = 2
    REMOVE_ROLES = 3
    ADD_BALANCE = 4
    REMOVE_BALANCE = 5
    ADD_ITEMS = 6
    REMOVE_ITEMS = 7

class ItemRequirement():
    def __init__(self, requirement_type: Union[int, ItemRequirementType], match_type: Union[int, ItemMatchType]=None, ids: Optional[list[int, str]]=None, balance: Optional[int]=None):
        self.type: ItemRequirementType = requirement_type if type(requirement_type) == ItemRequirementType else ItemRequirementType(requirement_type)
        self.match_type: Optional[ItemMatchType] = match_type if type(match_type) == ItemMatchType else (ItemMatchType(match_type) if match_type != None else None)
        self.ids: Optional[list[int]] = [int(id) if type(id) != int else id for id in ids] if ids else None
        self.balance: Optional[int] = balance

    def __repr__(self) -> str:
        if self.type == ItemRequirementType.TOTAL_BALANCE:
            return f"unbapi.ItemRequirement(type={self.type}, balance={self.balance})"
        else:
            return f"unbapi.ItemRequirement(type={self.type}, ids={self.ids})"
        
class ItemAction():
    def __init__(self, action_type: Union[int, ItemActionType], ids: Optional[list[int, str]]=None, balance: Optional[int]=None, message: Optional[str]=None):
        self.type: ItemActionType = action_type if type(action_type) == ItemActionType else ItemActionType(action_type)
        self.ids: Optional[list[int]] = [int(id) if type(id) != int else id for id in ids] if ids else None
        self.balance: Optional[int] = balance
        self.message: Optional[dict] = message

    def __repr__(self) -> str:
        if self.type in (ItemActionType.ADD_ROLES, ItemActionType.REMOVE_ROLES, ItemActionType.ADD_ITEMS, ItemActionType.REMOVE_ITEMS):
            return f"unbapi.ItemAction(type={self.type}, ids={self.ids})"
        elif self.type in (ItemActionType.ADD_BALANCE, ItemActionType.REMOVE_BALANCE):
            return f"unbapi.ItemAction(type={self.type}, balance={self.balance})"
        elif self.type == ItemActionType.RESPOND:
            return f"unbapi.ItemAction(type={self.type}, message={self.message})"
        else:
            return f"unbapi.ItemAction(type={self.type})"


class Item():
    def __init__(self, item_id: int, guild: "Guild", token: str, data: dict):
        self.id: int = item_id
        self.guild: Union[PartialGuild, Guild] = guild
        self.name: int = data["name"]
        self.price: Optional[int] = int(data["price"]) if data.get("price") else None
        self.description: Optional[str] = data.get("description")
        self.quantity: Optional[int] = int(data["quantity"]) if data.get("quantity") else None
        self.inventory_item: bool = data.get("is_inventory", True)
        self.usable: bool = data.get("is_usable", False)
        self.sellable: bool = data.get("is_sellable", False)
        self.stock_remaining: Optional[Union[int, "math.inf"]] = math.inf if data.get("unlimited_stock") else data.get("stock_remaining")
        self.expires_at: Optional[datetime] = datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None
        self.emoji: Optional[Union[str, int]] = int(data.get("emoji_id")) if data.get("emoji_id") else (data.get("unicode") if data.get("unicode") != "" else None)
        self.requirements: Optional[list[ItemRequirement]] = [ItemRequirement(requirement_type=requirement["type"], match_type=requirement.get("match_type"), ids=requirement.get("ids"), balance=requirement.get("balance")) for requirement in data["requirements"]] if type(data.get("requirements")) == list else None
        self.actions: Optional[list[ItemAction]] = [ItemAction(action_type=action["type"], ids=action.get("ids"), balance=action.get("balance"), message=action.get("message")) for action in data["actions"]] if type(data.get("actions")) == list else None
        self.__token = token

    def __repr__(self) -> str:
        if not self.quantity:
            return f"unbapi.Item(id={self.id}, name=\"{self.name}\")"
        else:
            return f"unbapi.Item(id={self.id}, name=\"{self.name}\", quantity={self.quantity})"

    def delete(self, include_inventories=False) -> None:
        """
        Deletes an item from the guild's store.

        :param include_inventories: To also delete this item from everyone's inventories. Defaults to False.
        """

        response = requests.delete(f"https://unbelievaboat.com/api/v1/guilds/{self.guild.id}/items/{self.id}", headers={
            "authorization": self.__token
        }, params={
            "cascade_delete": 'true' if include_inventories else 'false'
        })

        if response.status_code == 401: raise InvalidToken(response.json().get("message", "Token is not valid"))
        if response.status_code == 403: raise Forbidden(response.json().get("message", "This App is not allowed to access this resource"))
        if response.status_code == 404: raise NotFound(response.json().get("message", "Unkown Guild"))
        elif not response.ok: raise unbapiException(response.json().get("message", "HTTP request failed."))

        return None