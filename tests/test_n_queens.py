from nondeterministic.state_tree import StateTree
from nondeterministic.traversal import dfs

# a simple 8-queen solver using non-deterministic evaluation
def safe_n(n):
    def safe(rows):
        # rows: [r0, r1, r2, ..., rn]:
        #  -> queens' positions = [(0, r1), (1, r1), ..., (n, rn)]
        xc = len(rows)
        safe_rows = [
            r for r in range(n)
            if r not in rows
            if r not in [y + (xc - x) for x, y in enumerate(rows)]
            if r not in [y - (xc - x) for x, y in enumerate(rows)]
        ]
        return [rows + [r] for r in safe_rows]
    return safe


def n_queens(n=8):
    st = StateTree([[]], dfs())
    safe = safe_n(n)
    for _ in range(n):
        st.step(safe)
    return list(st)



def test_8_queens():
    assert len(n_queens(8)) == 92
