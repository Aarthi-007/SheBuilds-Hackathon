export type ContentType = "blog" | "ad" | "social_post" | "email" | "video_script" | "other";
export type Horizon = "30d" | "90d" | "1y";
export type Modality = "text" | "image";
export type Outlook = "improving" | "stable" | "declining" | "volatile";
export type Relevance = "supports" | "neutral" | "works_against";
export type Severity = "low" | "medium" | "high";

export interface ImpactSimulationRequest {
  company_id: string;
  modality: Modality;
  content?: string; // required for text; optional caption for image/video
  media?: string[]; // base64 data URLs — 1 image, or ordered video frames
  content_type: ContentType;
  horizon: Horizon;
  extra_context?: string;
}

export interface TrendSignal {
  trend: string;
  relevance: Relevance;
  explanation: string;
  source_url: string | null;
}

export interface RiskOrOpportunity {
  label: string;
  severity: Severity;
  explanation: string;
}

export interface PredictedTrajectory {
  outlook: Outlook;
  confidence_score: number;
  reasoning: string;
}

export interface ImpactSimulationReport {
  report_id: string;
  company_id: string;
  modality: Modality;
  perceived_description: string | null;
  horizon: string;
  summary: string;
  predicted_trajectory: PredictedTrajectory;
  trend_signals: TrendSignal[];
  risks: RiskOrOpportunity[];
  opportunities: RiskOrOpportunity[];
  recommendations: string[];
  citations: string[];
  created_at: string;
}
