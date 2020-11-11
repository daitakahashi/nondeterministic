
from typing import Callable, Generic, List, TypeVar

from .state_tree import StateTree

T = TypeVar('T')
O = TypeVar('O')


class Interpreter(Generic[T, O]):
    def __init__(
            self,
            f: Callable[[T, O], List[T]],
            initial_state: T
    ):
        self._f = f
        self._tree: StateTree[T] = StateTree([initial_state])

    @property
    def state(self) -> T:
        return self._tree.current

    def __iter__(self):
        return iter(self._tree)

    def interpret(self, observation: O) -> T:
        self._tree.step(lambda x: self._f(x, observation))
        return self.state
