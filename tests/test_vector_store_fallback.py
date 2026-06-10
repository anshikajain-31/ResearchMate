from langchain_core.documents import Document

from backend import vector_store


def test_add_paper_falls_back_to_local_store(monkeypatch):
    monkeypatch.setattr(vector_store, "get_vectorstore", lambda session_id: (_ for _ in ()).throw(RuntimeError("boom")))

    docs = [Document(page_content="Alpha beta", metadata={"title": "Demo Paper"})]

    vector_store.add_paper(docs, "session-123")

    assert vector_store.list_papers("session-123") == ["Demo Paper"]
