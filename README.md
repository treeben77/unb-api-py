# unb-api-py
unb-api-py allows python developers to use the UnbelievaBoat Discord bot API in their own projects! Here's how to get started:

(documentation is coming not-so-soon)

## Getting Started

1. Install the library
```console
pip install unbapi
```
2. Create an UnbelievaBoat Application at https://unbelievaboat.com/applications and copy the token (keep this secret)
3. Import the library, and create an `Application` object. Example:
```py
import unbapi

unbapp = unb.Application("put the token here from step 2.")
```
You've now created an `Application` object. This allows you to get or fetch a guild object. Here's how to get a guild object:
```py
guild = unbapp.get_guild(guild-id)
```
This will create `PartialGuild` object. This allows you to do every action in the guild but doesn't have much information about the app. If you need guild information, such as the name, icon, currency symbol, etc then you should use `unbapp.fetch_guild` which gives a `Guild` object. However, fetching information is slower then 'getting' it.

A `PartialGuild`, or `Guild` object allows you to do things inside of a guild (as long as you have permission), such as: fetching a user's balance (and changing it), getting store items, adding/removing items from user's inventories, and more. Here's how to do each:

## Examples

### Check the bot's permissions in a guild
```py
permissions = guild.fetch_permissions()
print(permissions.economy, permissions.items)
```

### Getting a user's balance
```py
user = guild.fetch_user(user-id)
print(user.cash, user.bank, user.total, user.rank)
```

### Updating a user's balance
This example will add 400 cash to their balance, and remove -100 bank from their bank balance.
```py
user.update_balance(cash=400, bank=-100)
```

### Setting a user's balance
This example set the users cash to 1000, and their bank balance to infinity
```py
import math

user.set_balance(cash=1000, bank=math.inf)
```

### Getting a list of all the items in a user's inventory
```py
for item in user.fetch_inventory():
  print(item.name, item.id, item.quantity)
```

### Check how much of an item a user has
```py
user.fetch_item_quantity(item-id)
```
(check out getting an item ID below)

### Add item to user inventory
```py
user.add_item(item-id, quantity=1)
```
(check out getting an item ID below)

### Remove item to user inventory
```py
user.remove_item(item-id, quantity=1)
```
(check out getting an item ID below)

### Get guild leaderboard
```py
for user in user.fetch_leaderboard():
  print(user.id, user.rank, user.total)
```

### Get guild store items
```py
for item in user.fetch_items():
  print(item.name, item.id, item.price)
```

### Delete guild item
```py
item.delete()
```
Editing guild items will come some time in the future.

## Exceptions
The library may raise these exceptions:
`unbapiException` Base exception for the library
`NotFound` The resource couldn't be found
`InvalidToken` The provided token isn't valid
`Forbidden` The bot can't access this
`TypeError` For a function that accepts `ObjectWithIdAttribute`, the provided object doesn't have an `id` attribute.

## Getting an Item Id
1. Use the `/item info` command from unbelivaboat
2. Click the blue command text after '<your name> used'
3. Copy the long string of numbers in the popup. Example:
![image](https://github.com/TreeBen77/unb-api-py/assets/77905642/0ae5a404-2e72-48a4-bbeb-38bf06254d38)
