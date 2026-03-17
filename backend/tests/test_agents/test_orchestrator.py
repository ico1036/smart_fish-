import pytest
from app.agents.orchestrator import PipelineOrchestrator, PipelineResult, PIPELINE_STAGES


def test_pipeline_stages_exist():
    assert "ontology" in PIPELINE_STAGES
    assert "graph" in PIPELINE_STAGES
    assert "simulation" in PIPELINE_STAGES
    assert "report" in PIPELINE_STAGES


def test_stage_order():
    orch = PipelineOrchestrator()
    order = orch.get_stage_order()
    assert order.index("ontology") < order.index("graph")
    assert order.index("graph") < order.index("simulation")
    assert order.index("simulation") < order.index("report")


def test_validate_pipeline():
    orch = PipelineOrchestrator()
    errors = orch.validate_pipeline()
    assert len(errors) == 0


def test_progress_callback():
    orch = PipelineOrchestrator()
    calls = []
    orch.set_progress_callback(lambda stage, prog, msg: calls.append((stage, prog, msg)))
    import asyncio
    asyncio.run(orch.run_stage("ontology", {}))
    assert len(calls) == 2  # start + complete
    assert calls[0][0] == "ontology"


@pytest.mark.asyncio
async def test_run_pipeline():
    orch = PipelineOrchestrator()
    result = await orch.run_pipeline(["test.pdf"], "Test requirement")
    assert result.success is True
    assert len(result.stages_completed) == 4
    assert "ontology" in result.results


@pytest.mark.asyncio
async def test_run_stage_unknown():
    orch = PipelineOrchestrator()
    with pytest.raises(ValueError, match="Unknown stage"):
        await orch.run_stage("nonexistent", {})


@pytest.mark.asyncio
async def test_run_stage_returns_result():
    orch = PipelineOrchestrator()
    result = await orch.run_stage("graph", {"file_paths": ["test.pdf"]})
    assert result["stage"] == "graph"
    assert result["status"] == "pending_sdk_integration"
