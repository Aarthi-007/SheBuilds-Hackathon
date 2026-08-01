from dataclasses import dataclass, field
from config.constants import (
    AGENT_PERCEPTION, AGENT_BRAND_IDENTITY, AGENT_DRIFT, AGENT_TREND,
    AGENT_PREDICTION, AGENT_OPTIMIZATION, AGENT_COMPLIANCE, AGENT_COPYRIGHT,
    AGENT_SAFETY, AGENT_CONTINUOUS_LEARNING,
    WORKFLOW_FULL_INGEST, WORKFLOW_QUICK_DRIFT, WORKFLOW_OPTIMIZE_ONLY, WORKFLOW_COMPETITOR_SCAN,
)


@dataclass
class TaskNode:
    agent_name: str
    depends_on: list[str] = field(default_factory=list)


TaskGraph = list[TaskNode]


def build_graph(workflow: str) -> TaskGraph:
    if workflow == WORKFLOW_FULL_INGEST:
        return [
            TaskNode(AGENT_PERCEPTION),
            TaskNode(AGENT_BRAND_IDENTITY, depends_on=[AGENT_PERCEPTION]),
            TaskNode(AGENT_DRIFT, depends_on=[AGENT_BRAND_IDENTITY]),
            TaskNode(AGENT_TREND, depends_on=[AGENT_BRAND_IDENTITY]),
            TaskNode(AGENT_PREDICTION, depends_on=[AGENT_DRIFT]),
            TaskNode(AGENT_OPTIMIZATION, depends_on=[AGENT_PREDICTION]),
            # compliance/copyright/safety can run concurrently after optimization
            TaskNode(AGENT_COMPLIANCE, depends_on=[AGENT_OPTIMIZATION]),
            TaskNode(AGENT_COPYRIGHT, depends_on=[AGENT_OPTIMIZATION]),
            TaskNode(AGENT_SAFETY, depends_on=[AGENT_OPTIMIZATION]),
            TaskNode(AGENT_CONTINUOUS_LEARNING, depends_on=[AGENT_COMPLIANCE, AGENT_COPYRIGHT, AGENT_SAFETY]),
        ]
    elif workflow == WORKFLOW_QUICK_DRIFT:
        return [
            TaskNode(AGENT_PERCEPTION),
            TaskNode(AGENT_DRIFT, depends_on=[AGENT_PERCEPTION]),
        ]
    elif workflow == WORKFLOW_OPTIMIZE_ONLY:
        return [
            TaskNode(AGENT_PERCEPTION),
            TaskNode(AGENT_OPTIMIZATION, depends_on=[AGENT_PERCEPTION]),
            TaskNode(AGENT_COMPLIANCE, depends_on=[AGENT_OPTIMIZATION]),
            TaskNode(AGENT_COPYRIGHT, depends_on=[AGENT_OPTIMIZATION]),
            TaskNode(AGENT_SAFETY, depends_on=[AGENT_OPTIMIZATION]),
        ]
    elif workflow == WORKFLOW_COMPETITOR_SCAN:
        return [
            TaskNode(AGENT_TREND),
            TaskNode(AGENT_BRAND_IDENTITY, depends_on=[AGENT_TREND]),
            TaskNode(AGENT_CONTINUOUS_LEARNING, depends_on=[AGENT_BRAND_IDENTITY]),
        ]
    else:
        raise ValueError(f"Unknown workflow: {workflow}")
