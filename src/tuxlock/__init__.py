##################################################
# Tuxlock - https://github.com/cibero42/tuxlock/ #
##################################################

from importlib import resources

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

__version__ = "0.1.0"

_cfg = tomllib.loads(resources.read_text("reader", "config.toml"))
URL = _cfg["feed"]["url"]