from orchestrator.task_graph import build_graph, TaskGraph


def plan(workflow: str) -> TaskGraph:
    """Return the TaskGraph for a given workflow type."""
    return build_graph(workflow)
