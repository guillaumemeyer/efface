import pytest

from efface.evaluate.splits import split_documents, split_records


def test_split_is_deterministic():
    docs = [f"doc-{i}" for i in range(10)]
    first = split_documents(docs, fraction=0.6, seed=7)
    second = split_documents(reversed(docs), fraction=0.6, seed=7)
    assert first == second
    assert (len(first[0]), len(first[1])) == (6, 4)


def test_split_is_disjoint_and_complete():
    docs = {f"doc-{i}" for i in range(37)}
    search, holdout = split_documents(docs, fraction=0.6, seed=11)
    assert set(search).isdisjoint(holdout)
    assert set(search) | set(holdout) == docs


def test_seed_changes_assignment():
    docs = [f"doc-{i}" for i in range(20)]
    assert split_documents(docs, fraction=0.5, seed=1) != split_documents(
        docs, fraction=0.5, seed=2
    )


def test_single_document_goes_to_search():
    assert split_documents(["only"], fraction=0.6) == (["only"], [])


def test_rejects_bad_fraction():
    with pytest.raises(ValueError):
        split_documents(["a"], fraction=0.0)


def test_split_records_keeps_documents_together():
    records = [{"doc": f"d{i}", "key": k} for i in range(10) for k in range(3)]
    search, holdout = split_records(records, key=lambda r: r["doc"], fraction=0.6, seed=5)
    search_docs = {r["doc"] for r in search}
    holdout_docs = {r["doc"] for r in holdout}
    assert search_docs.isdisjoint(holdout_docs)
    assert len(search) + len(holdout) == len(records)
