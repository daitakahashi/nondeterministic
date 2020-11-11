from typing import List

from nondeterministic.state_tree import StateTree
from nondeterministic.traversal import bfs, dfs

GRAPH_EDGES = {
    'a': ['b', 'c'],
    'b': ['d'], # a -> b -> d -> b -> d -> ...
    'd': ['b'],
    'c': ['e', 'f'],
    'e': ['f'],
    'f': ['f'] # f is a goal
}


def guess(x: List[str]) -> List[List[str]]:
    return [
        x + [y] for y in GRAPH_EDGES[x[-1]]
    ]


def is_completed(x: List[str]):
    return x[-1] == 'f'


def test_dfs_does_not_find_the_goal():
    st = StateTree([['a']], dfs())
    for _ in range(20):
        st.step(guess)
        assert not is_completed(st.current)


def test_bfs_finds_the_goal_in_2_steps():
    st = StateTree([['a']], bfs(is_completed))
    for _ in range(2):
        st.step(guess)
    assert is_completed(st.current)
    assert st.current == ['a', 'c', 'f']
