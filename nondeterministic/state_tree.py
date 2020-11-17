import itertools as it
from typing import (Callable, Generic, Iterable, Iterator, List, Optional,
                    TypeVar)

T = TypeVar('T')
O = TypeVar('O')

class StateTree(Generic[T]):
    def __init__(
            self,
            initial_states: Iterable[T],
            searcher: Optional[Callable[[Iterable[T]], Iterable[T]]] = None
    ):
        iter_state = iter(initial_states)
        self._evaluated: List[T] = []
        self._rest: Iterator[T] = iter_state
        self._searcher = searcher if searcher is not None else lambda x: x

    def _peek(self):
        if not self._evaluated:
            self._evaluated.append(next(self._rest))

    def __bool__(self) -> bool:
        try:
            self._peek()
            return True
        except StopIteration:
            return False

    @property
    def current(self) -> T:
        try:
            self._peek()
        except StopIteration as exc:
            raise RuntimeError('exhausted') from exc
        return self._evaluated[0]

    def __iter__(self) -> Iterator[T]:
        if self._evaluated:
            yield self._evaluated.pop()
        yield from self._rest

    def step(self, f: Callable[[T], Iterable[T]]):
        tree = it.chain.from_iterable(it.chain(
            map(f, self._evaluated), map(f, self._rest)
        ))
        self._evaluated = []
        self._rest = iter(self._searcher(tree))
