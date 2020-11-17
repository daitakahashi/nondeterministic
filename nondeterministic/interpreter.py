
from typing import Callable, Generic, Iterable, Iterator, TypeVar

from .state_tree import StateTree

T = TypeVar('T')
O = TypeVar('O')


class Interpreter(Generic[T, O]):
    def __init__(
            self,
            f: Callable[[T, O], Iterable[T]],
            initial_state: T
    ):
        self._f = f
        self._tree: StateTree[T] = StateTree([initial_state])

    def is_unique(self) -> bool:
        return self._tree.is_unique()

    def __bool__(self) -> bool:
        return bool(self._tree)

    @property
    def state(self) -> T:
        return self._tree.current

    def __iter__(self) -> Iterator[T]:
        return iter(self._tree)

    def interpret(self, observation: O):
        self._tree.step(lambda x: self._f(x, observation))
