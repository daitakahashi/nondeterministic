
import pytest

from nondeterministic.interpreter import Interpreter
from nondeterministic.state_tree import StateTree


def test_state_tree():
    # [1, 2, 3]
    #   >>= (\ x -> [x + 1, x - 1])
    #   >>= (\ x -> if x <= 2 then [] else [x])
    #
    # [1,    2,    3   ]
    #  | \   | \   | \
    # [2, 0, 3, 1, 4, 2]
    #  x  x  |  x  |  x
    # [      3,    4   ]
    #
    st = StateTree([1, 2, 3])
    st.step(lambda x: [x + 1, x - 1])
    st.step(lambda x: [] if x <= 2 else [x])
    # accessing to st.rest: only for testing purpose
    assert list(st) == [3, 4]


def test_delayed_evaluation():
    msg = 'asdffdafsdasas'
    def raise_error(x):
        if x > 0:
            raise RuntimeError(msg)
        return [x]
    st = StateTree([1, 2, 3])
    st.step(raise_error) # delayed
    with pytest.raises(RuntimeError) as excinfo:
        _ = st.current # evaluate f and raise an error
    assert str(excinfo.value) == msg


def test_state_tree_many_possiblities():
    st = StateTree([1, 2, 3])
    for _ in range(50):
        # 3^50 ~ 7*10^23 possilbilities
        st.step(lambda x: [x + 1, x, x - 1])
    assert st.current == 51
    assert next(iter(st)) == 51 # == current
    assert next(iter(st)) == 50
    st.step(lambda x: [] if x > 30 else [30])
    assert st.current == 30


# a very simple "guessing game"
# 1. a state is an integer
# 2. the initial state is 0
# 3. for each step, the state moves by -1, 0, or +1 from the current state
# 4. observations are inperfect; when an observation returns k,
#    the true state is one of k-1, k, and k+1 with scores 1, 8, and 1,
#    respectively

# state format: (current state, score)
def from_highest_score(state_scores):
    return sorted(state_scores, key=lambda x: x[1], reverse=True)

def drop_score(state_scores):
    return state_scores[0]

def guess(current, observation):
    current = drop_score(current)
    possible_from_observation = list(zip(
        [observation - 1, observation, observation + 1],
        [1, 8, 1]
    ))
    return from_highest_score([
        x for x in possible_from_observation
        if abs(x[0] - current) <= 1
    ])

@pytest.fixture(scope='function', name='interpreter')
def _interpreter():
    return Interpreter(guess, (0, 1))


def test_zero(interpreter):
    input_seq = [0, 0, 0]
    expected = [0, 0, 0]
    for x, y in zip(input_seq, expected):
        interpreter.interpret(x)
        assert drop_score(interpreter.state) == y


def test_backtrack(interpreter):
    input_seq = [0, 0, 2]
    expected = [0, 0, 1] # not 2, because scores are sorted locally
    for x, y in zip(input_seq, expected):
        interpreter.interpret(x)
        assert drop_score(interpreter.state) == y

#      0    0    3
# 0 -> 0 -> 0 -> x
#        -> 1 -> 2 ok
def test_backtrack2(interpreter):
    input_seq = [0, 0, 3]
    expected = [0, 0, 2] # not 3, because scores are sorted locally
    for x, y in zip(input_seq, expected):
        interpreter.interpret(x)
        assert drop_score(interpreter.state) == y


def test_unsatisfiable(interpreter):
    input_seq = [0, 0]
    for x in input_seq:
        interpreter.interpret(x)
    assert drop_score(interpreter.state) == 0
    with pytest.raises(RuntimeError):
        # it is impossible to observe 4 after [0, 0]
        interpreter.interpret(4)


def test_long_run(interpreter):
    # state evaluation is lazy, so we don't need extreme amount of space
    last_obs = 1000
    input_seq = list(range(last_obs + 1))
    for x in input_seq:
        interpreter.interpret(x)
    assert abs(drop_score(interpreter.state) - last_obs) <= 1


# we can embed a game history into a state
#  - T = List[int]
#  - O = int
def guess_hist(current, observation):
    state, score = current
    current_state = state[-1]
    possible_from_observation = list(zip(
        [observation - 1, observation, observation + 1],
        [1, 8, 1]
    ))
    return from_highest_score([
        (state + [x[0]], score + x[1]) for x in possible_from_observation
        if abs(x[0] - current_state) <= 1
    ])

@pytest.fixture(scope='function', name='interpreter_hist')
def _interpreter_hist():
    return Interpreter(guess_hist, ([0], 0))


def test_backtrack2_with_hist(interpreter_hist):
    input_seq = [0, 0, 3]
    expected = [
        [0, 0],      # <- 0
        [0, 0, 0],   # <- 0
        [0, 0, 1, 2] # <- 3: backtracked
    ]
    for x, y in zip(input_seq, expected):
        interpreter_hist.interpret(x)
        assert drop_score(interpreter_hist.state) == y


def test_get_all_solutions_with_hist(interpreter_hist):
    input_seq = [0, 0, 3]
    expected_state = [0, 0, 1, 2]
    expected_final_results = sorted([
        #    0  0  3 : input values
        ([0, 0, 1, 2], 0 + 8 + 1 + 1), # total score = 10
        ([0, 1, 1, 2], 0 + 1 + 1 + 1)  # total score = 3
    ], key=lambda x: x[1])
    for x in input_seq:
        interpreter_hist.interpret(x)
    assert drop_score(interpreter_hist.state) == expected_state
    # interpreter.finalize() returns iterator iterating over
    # all possible game sequences and closes itself.
    final_results = list(interpreter_hist)
    assert expected_final_results == sorted(
        final_results, key=lambda x: x[1]
    )
    # internal states are exhausted
    with pytest.raises(RuntimeError):
        _ = interpreter_hist.state
    with pytest.raises(RuntimeError):
        interpreter_hist.interpret(3)
    assert list(interpreter_hist) == []
