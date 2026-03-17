"""
SmartFish Orchestrator - coordinates the multi-agent pipeline.

This module defines the pipeline structure. When claude-agent-sdk is available,
these configs will be converted to AgentDefinition and ClaudeAgentOptions objects.
For now, this serves as the central pipeline coordinator.
"""

from dataclasses import dataclass, field
from typing import Callable, Any

from .ontology_agent import ONTOLOGY_AGENT_CONFIG
from .graph_agent import GRAPH_AGENT_CONFIG
from .report_agent import REPORT_AGENT_CONFIG


@dataclass
class PipelineStage:
    """Represents a stage in the SmartFish pipeline."""
    name: str
    description: str
    agent_config: dict
    depends_on: list[str] = field(default_factory=list)


@dataclass
class PipelineResult:
    """Result from a pipeline execution."""
    success: bool
    stages_completed: list[str] = field(default_factory=list)
    results: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


# Define the pipeline stages
PIPELINE_STAGES = {
    "ontology": PipelineStage(
        name="ontology",
        description="Analyze documents and generate ontology",
        agent_config=ONTOLOGY_AGENT_CONFIG,
        depends_on=[],
    ),
    "graph": PipelineStage(
        name="graph",
        description="Build knowledge graph from text using ontology",
        agent_config=GRAPH_AGENT_CONFIG,
        depends_on=["ontology"],
    ),
    "simulation": PipelineStage(
        name="simulation",
        description="Run multi-agent social media simulation",
        agent_config={},  # Dynamic - created per agent
        depends_on=["graph"],
    ),
    "report": PipelineStage(
        name="report",
        description="Generate analysis report from simulation results",
        agent_config=REPORT_AGENT_CONFIG,
        depends_on=["simulation"],
    ),
}


class PipelineOrchestrator:
    """Orchestrates the SmartFish multi-agent pipeline."""

    def __init__(self):
        self.stages = PIPELINE_STAGES
        self._progress_callback: Callable | None = None

    def set_progress_callback(self, callback: Callable):
        """Set a callback for progress updates: callback(stage_name, progress, message)"""
        self._progress_callback = callback

    def _notify_progress(self, stage: str, progress: float, message: str):
        if self._progress_callback:
            self._progress_callback(stage, progress, message)

    def get_stage_order(self) -> list[str]:
        """Return stages in dependency order."""
        # Simple topological sort for our linear pipeline
        order = []
        visited = set()

        def visit(name):
            if name in visited:
                return
            stage = self.stages[name]
            for dep in stage.depends_on:
                visit(dep)
            visited.add(name)
            order.append(name)

        for name in self.stages:
            visit(name)
        return order

    def validate_pipeline(self) -> list[str]:
        """Validate pipeline configuration. Returns list of errors."""
        errors = []
        for name, stage in self.stages.items():
            for dep in stage.depends_on:
                if dep not in self.stages:
                    errors.append(f"Stage '{name}' depends on unknown stage '{dep}'")
            if not stage.description:
                errors.append(f"Stage '{name}' missing description")
        return errors

    async def run_stage(self, stage_name: str, context: dict) -> dict:
        """
        Run a single pipeline stage.

        In production, this will:
        1. Create an AgentDefinition from the stage config
        2. Create MCP servers for the tools
        3. Run the agent via ClaudeSDKClient
        4. Return the result

        For now, returns a placeholder.
        """
        if stage_name not in self.stages:
            raise ValueError(f"Unknown stage: {stage_name}")

        stage = self.stages[stage_name]
        self._notify_progress(stage_name, 0.0, f"Starting {stage.description}")

        # TODO: Wire up claude-agent-sdk here
        result = {
            "stage": stage_name,
            "status": "pending_sdk_integration",
            "agent_config": stage.agent_config,
            "context": context,
        }

        self._notify_progress(stage_name, 1.0, f"Completed {stage.description}")
        return result

    async def run_pipeline(
        self, file_paths: list[str], simulation_requirement: str
    ) -> PipelineResult:
        """
        Run the full pipeline.

        For now, validates and returns the pipeline structure.
        Full execution requires claude-agent-sdk integration.
        """
        errors = self.validate_pipeline()
        if errors:
            return PipelineResult(success=False, error="; ".join(errors))

        context = {
            "file_paths": file_paths,
            "simulation_requirement": simulation_requirement,
        }

        result = PipelineResult(success=True)
        for stage_name in self.get_stage_order():
            stage_result = await self.run_stage(stage_name, context)
            result.stages_completed.append(stage_name)
            result.results[stage_name] = stage_result

        return result
