"""
Singleton factory for the OrchestratorAgent and all registered agents.
Import get_orchestrator() wherever an orchestrator instance is needed.
"""
from orchestrator.orchestrator_agent import OrchestratorAgent
from agents.perception_agent import PerceptionAgent
from agents.brand_identity_agent import BrandIdentityAgent
from agents.identity_drift_agent import IdentityDriftAgent
from agents.trend_intelligence_agent import TrendIntelligenceAgent
from agents.predictive_intelligence_agent import PredictiveIntelligenceAgent
from agents.optimization_agent import OptimizationAgent
from agents.compliance_agent import ComplianceAgent
from agents.copyright_agent import CopyrightAgent
from agents.safety_agent import SafetyAgent
from agents.continuous_learning_agent import ContinuousLearningAgent
from config.constants import (
    AGENT_PERCEPTION, AGENT_BRAND_IDENTITY, AGENT_DRIFT, AGENT_TREND,
    AGENT_PREDICTION, AGENT_OPTIMIZATION, AGENT_COMPLIANCE, AGENT_COPYRIGHT,
    AGENT_SAFETY, AGENT_CONTINUOUS_LEARNING,
)

_orchestrator: OrchestratorAgent | None = None


def get_orchestrator() -> OrchestratorAgent:
    global _orchestrator
    if _orchestrator is None:
        agents = {
            AGENT_PERCEPTION: PerceptionAgent(),
            AGENT_BRAND_IDENTITY: BrandIdentityAgent(),
            AGENT_DRIFT: IdentityDriftAgent(),
            AGENT_TREND: TrendIntelligenceAgent(),
            AGENT_PREDICTION: PredictiveIntelligenceAgent(),
            AGENT_OPTIMIZATION: OptimizationAgent(),
            AGENT_COMPLIANCE: ComplianceAgent(),
            AGENT_COPYRIGHT: CopyrightAgent(),
            AGENT_SAFETY: SafetyAgent(),
            AGENT_CONTINUOUS_LEARNING: ContinuousLearningAgent(),
        }
        _orchestrator = OrchestratorAgent(agents=agents)
    return _orchestrator
