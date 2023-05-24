from .application import *
from .guild import *
from .user import *
from .items import *

from typing import Literal

VERSION: str = "0.1.0"
VERSION_INFO: Literal['alpha', 'beta', 'final'] = "alpha"

del Literal
