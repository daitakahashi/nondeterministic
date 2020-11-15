import re

from nondeterministic.state_tree import StateTree


def choose(sym):
    def _choose(state):
        nums, condition, carry = state
        if sym == ' ' or sym in nums:
            return [state]
        return [
            ({sym: num, **nums}, condition, carry)
            for num in range(10)
            if num not in nums.values()
            if sym not in condition or condition[sym](num)
        ]
    return _choose

def add(sym_z, sym_xs):
    # sym_z = sum(sym_xs) (ignoring carry)
    def _add(state):
        nums, condition, carry = state
        sum_xs = sum(
            0 if sym == ' ' else nums[sym]
            for sym in sym_xs
        )
        carry, z = divmod(sum_xs + carry, 10)
        if sym_z not in nums \
           and z not in nums.values() \
           and (sym_z not in condition or condition[sym_z](z)):
            return [({sym_z: z, **nums}, condition, carry)]
        if sym_z in nums and z == nums[sym_z]:
            return [(nums, condition, carry)] # update carry
        return []
    return _add

def assert_state(pred):
    def _assert_state(state):
        if pred(state):
            return [state]
        return []
    return _assert_state

def no_carry(state):
    _, _, carry = state
    return carry == 0

def is_positive(x):
    return x > 0

def check_solution(eq, solution):
    trans = str.maketrans({
        key: str(value) for key, value in solution.items()
    })
    nums = [int(line.translate(trans).strip()) for line in eq]
    return sum(nums[:-1]) == nums[-1]


# two examples from wikipedia
def test_sendmoremoney():
    eq = [' send',
          ' more',
          'money']
    heads = ['s', 'm']
    st = StateTree([({}, {h: is_positive for h in heads}, 0)])
    code = [
        choose('d'), choose('e'), add('y', ['d', 'e']),
        choose('n'), choose('r'), add('e', ['n', 'r']),
        choose('o'), add('n', ['e', 'o']),
        choose('s'), choose('m'), add('o', ['s', 'm']),
        add('m', [' ', ' ']),
        assert_state(no_carry) # trivial, but for consistency
    ]
    for instr in code:
        st.step(instr)
    for solution, _, _ in st:
        assert check_solution(eq, solution)


def test_long_eq():
    # An example of how late failures impact performance.
    #
    # On this long equation, there are only a few chances of backtracking,
    # and we need to choose most of numbers before the first failure
    # (indeed, we need to choose 8 numbers before the first add()).
    # As a result, an *unevaluated* search tree grows to extreme size,
    # and travarsal of the tree takes long period of time
    # (with roughly constant amount of space).
    #
    # It takes approx. 30sec (and 35MB of RAM) on MacbookAir with 1.4Ghz CPU.
    eq = 'SO+MANY+MORE+MEN+SEEM+TO+SAY+THAT+' \
        'THEY+MAY+SOON+TRY+TO+STAY+AT+HOME+' \
        'SO+AS+TO+SEE+OR+HEAR+THE+SAME+ONE+' \
        'MAN+TRY+TO+MEET+THE+TEAM+ON+THE+' \
        'MOON+AS+HE+HAS+AT+THE+OTHER+TEN' \
        '=TESTS'
    eq = re.split('[+=]', eq)
    max_digits = max(len(num) for num in eq)
    eq = [num.rjust(max_digits, ' ') for num in eq]
    heads = {line.strip()[0] for line in eq}
    st = StateTree([({}, {h: is_positive for h in heads}, 0)])

    for z, *xs in reversed(list(zip(*reversed(eq)))):
        # add from lower digits to keep track of carries
        for x in xs:
            st.step(choose(x))
        st.step(add(z, xs))
    # check remaining carry is zero
    st.step(assert_state(no_carry))

    for solution, _, _ in list(st):
        assert check_solution(eq, solution)
