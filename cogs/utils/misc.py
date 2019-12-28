import discord
from typing import Union

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