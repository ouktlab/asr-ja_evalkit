from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("asr-ja_evalkit")
except PackageNotFoundError:
    __version__ = "unknown"

from .app import app_pyscliteja as app_pyscliteja
from .app import app_preprocess as app_preprocess
from .app import app_postprocess as app_postprocess
