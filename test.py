from tippspiel import score

real1 = 3, 0
real2 = 0, 3


def test_score():
    assert score((1, 0), real1) == 1
    assert score((3, 0), real1) == 3
    assert score((0, 3), real1) == 0
    assert score((1, 0), real2) == 0
    assert score((0, 1), real2) == 1
    assert score((1, 1), real2) == 0
    assert score((1, 1), (2, 2)) == 1
