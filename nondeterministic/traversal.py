
import heapq
from typing import Any, Callable, Iterable, TypeVar

T = TypeVar('T')

def dfs() -> Callable[[Iterable[T]], Iterable[T]]:
    return lambda x: x

def bfs(is_finished: Callable[[T], Any]) -> Callable[[Iterable[T]], Iterable[T]]:
    return lambda x: sorted(x, key=is_finished, reverse=True)

def beam(k: int, key: Callable[[T], Any]) -> Callable[[Iterable[T]], Iterable[T]]:
    return lambda x: heapq.nlargest(k, x, key=key)
