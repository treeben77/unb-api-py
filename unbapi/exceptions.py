__all__ = (
    "unbapiException",
    "NotFound",
    "InvalidToken",
    "Forbidden"
)

class unbapiException(Exception): pass
class NotFound(unbapiException): pass
class InvalidToken(unbapiException): pass
class Forbidden(unbapiException): pass