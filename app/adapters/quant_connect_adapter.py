import datetime
from pyparsing import Iterator
from .base_adapter import BaseAdapter
import os
import json
from datetime import datetime as _dt


class QuantConnectAdapter(BaseAdapter):
    """Adapter for quant connect datasets."""
