class ScoringService:
    def compute_drift_score(
        self,
        brand_similarity: float,
        competitor_similarities: list[float],
    ) -> float:
        """
        Drift score: 0 = perfectly on-brand, 1 = maximum drift.
        High brand similarity → low drift.
        High competitor similarity → higher drift.
        """
        avg_competitor = sum(competitor_similarities) / len(competitor_similarities) if competitor_similarities else 0.0
        drift = (1.0 - brand_similarity) * 0.6 + avg_competitor * 0.4
        return round(min(max(drift, 0.0), 1.0), 4)

    def compute_distinctiveness(
        self,
        brand_similarity: float,
        competitor_similarities: list[float],
    ) -> float:
        """How different this content is from all competitors (0–1, higher = more distinctive)."""
        avg_competitor = sum(competitor_similarities) / len(competitor_similarities) if competitor_similarities else 0.0
        return round(1.0 - avg_competitor, 4)

    def compute_prediction_features(
        self,
        drift_score: float,
        brand_similarity: float,
        trend_alignment: float = 0.5,
    ) -> dict:
        """Simple heuristic features as inputs to Claude's prediction reasoning."""
        return {
            "drift_score": drift_score,
            "brand_similarity": brand_similarity,
            "trend_alignment": trend_alignment,
            "estimated_engagement_base": round((brand_similarity * 0.5 + trend_alignment * 0.5), 4),
        }
