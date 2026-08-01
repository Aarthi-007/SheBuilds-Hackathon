import asyncio
from dataclasses import dataclass
from pydantic import BaseModel
from typing import Any

from agents.base_agent import BaseAgent
from orchestrator.planner import plan
from orchestrator.task_graph import TaskGraph, TaskNode
from orchestrator.retry_policy import run_with_retry
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ReflectionNotes:
    completed: list[str]
    failed: list[str]
    warnings: list[str]


class OrchestratorRequest(BaseModel):
    workflow: str
    inputs: dict  # keyed by agent_name or shared keys like "content", "company_id"


class OrchestratorResult(BaseModel):
    workflow: str
    results: dict  # agent_name -> result payload dict
    reflection: dict


class OrchestratorAgent:
    def __init__(self, agents: dict[str, BaseAgent]):
        self._agents = agents

    async def run(self, request: OrchestratorRequest) -> OrchestratorResult:
        graph = self._plan(request)
        results = await self._execute_graph(graph, request.inputs)
        reflection = self._reflect(results)
        return OrchestratorResult(
            workflow=request.workflow,
            results={k: (v.model_dump() if hasattr(v, "model_dump") else v) for k, v in results.items()},
            reflection={"completed": reflection.completed, "failed": reflection.failed, "warnings": reflection.warnings},
        )

    def _plan(self, request: OrchestratorRequest) -> TaskGraph:
        return plan(request.workflow)

    async def _execute_graph(self, graph: TaskGraph, inputs: dict) -> dict[str, Any]:
        completed: dict[str, Any] = {}
        failed: set[str] = set()

        # Topological execution with concurrency
        remaining = list(graph)

        while remaining:
            # Find all nodes whose dependencies are satisfied
            ready = [
                node for node in remaining
                if all(dep in completed for dep in node.depends_on)
                and node.agent_name not in failed
            ]

            if not ready:
                # Check if any blocked nodes remain — if so, they all depend on failed agents
                break

            # Run ready nodes concurrently
            tasks = {node.agent_name: self._run_node(node, completed, inputs) for node in ready}
            task_results = await asyncio.gather(*tasks.values(), return_exceptions=True)

            for agent_name, result in zip(tasks.keys(), task_results):
                if isinstance(result, Exception):
                    logger.error("Agent %s failed: %s", agent_name, result)
                    failed.add(agent_name)
                else:
                    completed[agent_name] = result
                    logger.info("Agent %s completed.", agent_name)

            remaining = [n for n in remaining if n.agent_name not in completed and n.agent_name not in failed]

        return completed

    async def _run_node(self, node: TaskNode, completed: dict, inputs: dict) -> Any:
        agent = self._agents.get(node.agent_name)
        if agent is None:
            raise ValueError(f"No agent registered for: {node.agent_name}")

        input_data = self._build_input(node.agent_name, completed, inputs)
        return await run_with_retry(agent, input_data)

    def _build_input(self, agent_name: str, completed: dict, inputs: dict) -> BaseModel:
        """Build typed input for each agent from accumulated results and initial inputs."""
        from agents.perception_agent import PerceptionInput
        from agents.brand_identity_agent import BrandIdentityInput
        from agents.identity_drift_agent import DriftInput
        from agents.trend_intelligence_agent import TrendInput
        from agents.predictive_intelligence_agent import PredictionInput
        from agents.optimization_agent import OptimizationInput
        from agents.compliance_agent import ComplianceInput
        from agents.copyright_agent import CopyrightInput
        from agents.safety_agent import SafetyInput
        from agents.continuous_learning_agent import ContinuousLearningInput

        perception = completed.get("perception")
        brand = completed.get("brand_identity") or inputs.get("brand_identity")
        drift = completed.get("drift")
        prediction = completed.get("prediction")
        optimization = completed.get("optimization")
        trend = completed.get("trend")

        if agent_name == "perception":
            return PerceptionInput(
                company_id=inputs["company_id"],
                modality=inputs["modality"],
                payload=inputs["payload"],
            )
        elif agent_name == "brand_identity":
            batch = [perception] if perception else inputs.get("content_batch", [])
            return BrandIdentityInput(company_id=inputs["company_id"], content_batch=batch)
        elif agent_name == "drift":
            return DriftInput(content=perception, brand_identity=brand)
        elif agent_name == "trend":
            return TrendInput(company_id=inputs["company_id"], brand_identity=brand)
        elif agent_name == "prediction":
            return PredictionInput(content=perception, brand_identity=brand, drift_report=drift)
        elif agent_name == "optimization":
            return OptimizationInput(content=perception, brand_identity=brand, drift_report=drift, prediction_report=prediction)
        elif agent_name == "compliance":
            content = optimization and type("_", (), {"content_id": perception.content_id, "flattened_text": optimization.optimized_text, "company_id": perception.company_id})()
            return ComplianceInput(content=perception, brand_identity=brand)
        elif agent_name == "copyright":
            return CopyrightInput(content=perception)
        elif agent_name == "safety":
            return SafetyInput(content=perception)
        elif agent_name == "continuous_learning":
            return ContinuousLearningInput(
                company_id=inputs["company_id"],
                content=perception,
                brand_identity=brand,
                trend_knowledge=trend,
                drift_report=drift,
                prediction_report=prediction,
            )
        else:
            raise ValueError(f"Unknown agent: {agent_name}")

    def _reflect(self, results: dict) -> ReflectionNotes:
        from config.constants import (
            AGENT_PERCEPTION, AGENT_BRAND_IDENTITY, AGENT_DRIFT,
            AGENT_PREDICTION, AGENT_OPTIMIZATION, AGENT_COMPLIANCE,
            AGENT_COPYRIGHT, AGENT_SAFETY,
        )
        completed = list(results.keys())
        expected = [AGENT_PERCEPTION, AGENT_BRAND_IDENTITY, AGENT_DRIFT,
                    AGENT_PREDICTION, AGENT_OPTIMIZATION, AGENT_COMPLIANCE,
                    AGENT_COPYRIGHT, AGENT_SAFETY]
        failed = [a for a in expected if a not in completed]
        warnings = [f"{a} did not complete" for a in failed]
        return ReflectionNotes(completed=completed, failed=failed, warnings=warnings)
