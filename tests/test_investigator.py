from investigator import GameGlitchInvestigator
from retrieval import KnowledgeRetriever, load_knowledge_base


def test_knowledge_base_loads_chunks():
    chunks = load_knowledge_base()
    assert len(chunks) >= 4
    assert any("session" in chunk.content.lower() for chunk in chunks)


def test_retriever_finds_state_context():
    retriever = KnowledgeRetriever()
    evidence = retriever.retrieve("secret number resets after submit")
    assert evidence
    assert evidence[0].score > 0


def test_investigator_classifies_hint_logic(tmp_path):
    investigator = GameGlitchInvestigator(log_path=tmp_path / "log.jsonl")
    result = investigator.investigate(
        "The hint says go higher when my guess is already too high."
    )
    assert result.category == "hint_logic"
    assert result.confidence >= 0.65
    assert result.retrieved_sources


def test_investigator_guardrail_for_vague_report(tmp_path):
    investigator = GameGlitchInvestigator(log_path=tmp_path / "log.jsonl")
    result = investigator.investigate("bad")
    assert result.guardrail_triggered is True
    assert result.category == "needs_more_context"


def test_investigator_writes_audit_log(tmp_path):
    log_path = tmp_path / "investigations.jsonl"
    investigator = GameGlitchInvestigator(log_path=log_path)
    investigator.investigate("The score display lags behind after I submit a guess.")
    assert log_path.exists()
    assert "render_order" in log_path.read_text()
