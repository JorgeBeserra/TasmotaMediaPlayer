from __future__ import annotations

import urllib
from asyncio.transports import BaseTransport
from typing import Awaitable, Tuple
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

import aiohttp

#from aiomusiccast.exceptions import MusicCastConnectionException, MusicCastConfigurationException, MusicCastParamException

import json
import logging
import queue
from datetime import datetime
from aiohttp import ClientError, ClientTimeout, ClientResponse
import asyncio

BAND = ['common', 'am', 'fm', 'dab']


_LOGGER = logging.getLogger(__name__)