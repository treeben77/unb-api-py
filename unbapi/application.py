import requests, base64, json
from typing import Union, TypeVar

from .exceptions import InvalidToken, NotFound
from .guild import PartialGuild, Guild

__all__ = (
    "Application",
)

class Application():
    def __init__(self, token: str):
        """
        Base object for interacting with the UnbelievaBoat API.

        :param token: Your application's token from https://unbelievaboat.com/applications
        """
        self.__token = token
        self.id = json.loads(base64.urlsafe_b64decode(self.__token.split(".")[1] + '=='))["app_id"]

    def __repr__(self) -> str:
        return f"unbapi.Application(id={self.id})"

    def get_guild(self, guild_id: Union[int, str, TypeVar("ObjectWithIdAttribute")]) -> PartialGuild:
        """
        Generates a PartialGuild object without querying the API. The partial Guild object will not include any metadata.

        :param guild_id: The guild id either as an int, str, or an object with an `id` attribute (such as discord.py's Guild object).
        """
        if type(guild_id) == str:
            guild_id = int(guild_id)
        elif not type(guild_id) == int:
            try:
                guild_id = guild_id.id
            except(AttributeError):
                raise TypeError("guild_id object doesn't have an id attribute.")
        
        return PartialGuild(guild_id, self, self.__token)

    def fetch_guild(self, guild_id: Union[int, str, TypeVar("ObjectWithIdAttribute")]) -> Guild:
        """
        Fetches information about the Guild and will return a Guild object which includes the Guild's name, icon, symbol, and other attributes.

        :param guild_id: The guild id either as an int, str, or an object with an `id` attribute (such as discord.py's Guild object).
        """

        if type(guild_id) == str:
            guild_id = int(guild_id)
        elif not type(guild_id) == int:
            try:
                guild_id = guild_id.id
            except(AttributeError):
                raise TypeError("guild_id object doesn't have an id attribute.")
        
        response = requests.get(f"https://unbelievaboat.com/api/v1/guilds/{guild_id}", headers={
            "authorization": self.__token
        })

        if response.status_code == 401: raise InvalidToken(response.json().get("message", "Token is not valid"))
        if response.status_code == 404: raise NotFound(response.json().get("message", "Unkown Guild"))

        return Guild(guild_id, self, self.__token, response.json())