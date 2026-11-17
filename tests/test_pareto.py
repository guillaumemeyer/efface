from efface.evaluate.pareto import pareto_frontier


def test_frontier_drops_dominated_points():
    points = [(0.8, 0.5), (0.9, 0.6), (0.7, 0.7)]
    assert pareto_frontier(points) == [1, 2]


def test_frontier_keeps_duplicates():
    points = [(0.5, 0.5), (0.5, 0.5)]
    assert pareto_frontier(points) == [0, 1]


def test_frontier_with_minimised_axis():
    points = [(1.0, 1.0), (0.5, 0.5)]
    assert pareto_frontier(points, maximize=(True, False)) == [0, 1]


def test_empty_frontier():
    assert pareto_frontier([]) == []
