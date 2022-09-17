import discord
from typing import Union, Sequence
import subprocess
from collections import namedtuple
from mcstatus import JavaServer as MinecraftServer
from base64 import b64decode
import re

def string_distance(a: str, b: str):
    """
    Returns the levenshtein distance between two strings, which can be used to compare their similarity
    
    [Code source](https://github.com/TheAlgorithms/Python/blob/master/strings/levenshtein_distance.py)
    """
    if len(a) < len(b): return string_distance(b, a)
    if len(b) == 0: return len(a)
    prow = range(len(b) + 1)
    for i, c1 in enumerate(a):
        crow = [i + 1]
        for j, c2 in enumerate(b):
            ins = prow[j + 1] + 1
            dl = crow[j] + 1
            sub = prow[j] + (c1 != c2)
            crow.append(min(ins, dl, sub))
        prow = crow
    return prow[-1]

def buttons_mixin(buttons):
    """
    Changes a function in the discord.ext.buttons library
    to instead of deleting the message, clear all the reactions (if possible)
    """
    async def _teardown(self, *args, **kwargs):
        """Clean the session up."""
        self._session_task.cancel()

        try:
            await self.page.clear_reactions()
        except discord.Forbidden:
            pass
    buttons.Session.teardown = _teardown

def safe_div(a: Union[int, float], b: Union[int, float], return_a: bool=True):
    if b == 0: return a if return_a else 0
    else: return a / b

ProcessInfo = namedtuple('ProcessInfo', ['out', 'err', 'ret'])

def run_command(cmd: Sequence[str], input: bool=None) -> ProcessInfo:
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate(input)
    ret = process.poll()
    return ProcessInfo(out, err, ret)

MinecraftInfo = namedtuple('MinecraftInfo', ['ping', 'desc', 'online', 'max', 'players', 'version', 'icon'])

def mcserver_status(server_ip: str, query: bool=False) -> MinecraftInfo:
    server = MinecraftServer.lookup(server_ip)
    if query:
        try:
            query = server.query(retries=1)
        except Exception:
            pass
        else:
            return MinecraftInfo(
                server.ping(retries=1),
                query.motd,
                query.players.online,
                query.players.max,
                query.players.names,
                query.software.version,
                None
            )
    try:
        status = server.status(retries=1)
    except Exception:
        pass
    else:
        icon = status.favicon
        if icon:
            icon = b64decode(icon.split(',')[1].encode())
        return MinecraftInfo(
            status.latency,
            status.description if isinstance(status.description, str) else status.description['text'],
            status.players.online,
            status.players.max,
            [p.name for p in status.players.sample or []],
            status.version.name,
            icon
        )

def parse_args(query: str, arg_prefix: str='--') -> dict:
    """
    Parse arguments unix style
    ```
    >>> parse_args('mat mat --hello world --no-val')
    ('mat mat', {'hello': 'world', 'no-val': None})
    ```
    """
    first = query.find(arg_prefix)
    args = {}
    if first != -1:
        for match in re.finditer(arg_prefix + r'([a-z-]+)(?: ([\w ]+))?', query):
            key, value = match.group(1, 2)
            args[key] = value
        return query[:first].rstrip(), args
    else:
        return query, args
