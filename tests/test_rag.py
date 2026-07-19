import pytest
from backend.rag.retrieval import retrieve

def test_retrieve_known():
    # Test known place/era returns non-empty, relevant content
    place = "Taxila"
    era = "Maurya Empire"
    content = retrieve(place, era)
    assert isinstance(content, str)
    assert len(content) > 50, "RAG content should be non-empty for known place/era"
    assert "Taxila" in content or "Maurya" in content

def test_retrieve_unknown():
    # Test unknown place/era returns empty string gracefully
    place = "UnknownCity"
    era = "UnknownEra"
    content = retrieve(place, era)
    assert content == "", "Unknown place/era should return empty string"
