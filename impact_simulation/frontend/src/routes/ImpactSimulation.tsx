import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { runImpactSimulation } from "../lib/api";
import { fileToDataUrl } from "../lib/media";
import type {
  ContentType,
  Horizon,
  ImpactSimulationReport,
  Modality,
  Severity,
} from "../lib/types";
import TrajectoryLine from "../components/charts/TrajectoryLine";

const SEVERITY_COLOR: Record<Severity, string> = {
  low: "text-muted border-line",
  medium: "text-warn border-warn/40",
  high: "text-danger border-danger/40",
};

export default function ImpactSimulation() {
  const [companyId, setCompanyId] = useState("demo-co");
  const [modality, setModality] = useState<Modality>("text");
  const [content, setContent] = useState("");
  const [contentType, setContentType] = useState<ContentType>("social_post");
  const [horizon, setHorizon] = useState<Horizon>("90d");
  const [extraContext, setExtraContext] = useState("");

  const [mediaFile, setMediaFile] = useState<File | null>(null);
  const [mediaPreviewUrl, setMediaPreviewUrl] = useState<string | null>(null);
  const [preparingMedia, setPreparingMedia] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<ImpactSimulationReport | null>(null);

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0] ?? null;
    setMediaFile(file);
    setMediaPreviewUrl(file ? URL.createObjectURL(file) : null);
  }

  function isReady() {
    if (modality === "text") return content.trim().length > 0;
    return mediaFile !== null;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!isReady()) return;
    setLoading(true);
    setError(null);
    setReport(null);

    try {
      let media: string[] | undefined;

      if (modality === "image" && mediaFile) {
        setPreparingMedia(true);
        media = [await fileToDataUrl(mediaFile)];
        setPreparingMedia(false);
      }

      const result = await runImpactSimulation({
        company_id: companyId,
        modality,
        content: content || undefined,
        media,
        content_type: contentType,
        horizon,
        extra_context: extraContext || undefined,
      });
      setReport(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Simulation failed. Try again.");
    } finally {
      setLoading(false);
      setPreparingMedia(false);
    }
  }

  return (
    <div className="min-h-screen bg-ink px-6 py-10 md:px-16">
      <header className="mb-10">
        <p className="font-mono text-xs uppercase tracking-[0.2em] text-signal mb-2">
          Klyro / Impact Simulation
        </p>
        <h1 className="font-display text-3xl md:text-4xl font-semibold text-paper">
          How will this content age?
        </h1>
        <p className="text-muted mt-2 max-w-2xl">
          Give Klyro a piece of AI-generated content. It researches current
          trends and reasons about how the content is likely to perform over
          time, then returns a full analysis.
        </p>
      </header>

      <div className="grid md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] gap-8">
        {/* ── Input panel ─────────────────────────────────────────── */}
        <form
          onSubmit={handleSubmit}
          className="bg-panel border border-line rounded-lg p-6 flex flex-col gap-5 h-fit"
        >
          {/* Modality toggle: text / image only */}
          <div>
            <label className="block text-xs font-mono uppercase tracking-wider text-muted mb-2">
              Content type
            </label>
            <div className="flex gap-2">
              {(["text", "image"] as Modality[]).map((m) => (
                <button
                  key={m}
                  type="button"
                  onClick={() => {
                    setModality(m);
                    setMediaFile(null);
                    setMediaPreviewUrl(null);
                  }}
                  className={`flex-1 py-2 rounded-md text-sm font-medium border transition capitalize ${
                    modality === m
                      ? "border-signal text-signal bg-signal/10"
                      : "border-line text-muted hover:text-paper"
                  }`}
                >
                  {m}
                </button>
              ))}
            </div>
          </div>

          {/* Text input */}
          {modality === "text" && (
            <div>
              <label className="block text-xs font-mono uppercase tracking-wider text-muted mb-2">
                Content
              </label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Paste the AI-generated content you want to simulate…"
                rows={8}
                className="w-full bg-ink border border-line rounded-md p-3 text-paper placeholder:text-muted/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-signal resize-y"
              />
            </div>
          )}

          {/* Image input */}
          {modality === "image" && (
            <div className="flex flex-col gap-4">
              <div>
                <label className="block text-xs font-mono uppercase tracking-wider text-muted mb-2">
                  Upload image
                </label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="w-full text-sm text-muted file:mr-3 file:py-2 file:px-3 file:rounded-md file:border-0 file:bg-signal file:text-ink file:font-medium file:cursor-pointer"
                />
              </div>

              {mediaPreviewUrl && (
                <img
                  src={mediaPreviewUrl}
                  alt="preview"
                  className="rounded-md border border-line max-h-48 object-cover"
                />
              )}

              <div>
                <label className="block text-xs font-mono uppercase tracking-wider text-muted mb-2">
                  Caption / accompanying copy{" "}
                  <span className="normal-case text-muted/70">(optional)</span>
                </label>
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="Any caption or copy that runs alongside this image…"
                  rows={3}
                  className="w-full bg-ink border border-line rounded-md p-3 text-paper placeholder:text-muted/60 resize-y"
                />
              </div>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-mono uppercase tracking-wider text-muted mb-2">
                Format
              </label>
              <select
                value={contentType}
                onChange={(e) => setContentType(e.target.value as ContentType)}
                className="w-full bg-ink border border-line rounded-md p-2.5 text-paper"
              >
                <option value="social_post">Social post</option>
                <option value="blog">Blog</option>
                <option value="ad">Ad</option>
                <option value="email">Email</option>
                <option value="video_script">Video script</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-mono uppercase tracking-wider text-muted mb-2">
                Time horizon
              </label>
              <select
                value={horizon}
                onChange={(e) => setHorizon(e.target.value as Horizon)}
                className="w-full bg-ink border border-line rounded-md p-2.5 text-paper"
              >
                <option value="30d">30 days</option>
                <option value="90d">90 days</option>
                <option value="1y">1 year</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono uppercase tracking-wider text-muted mb-2">
              Company ID
            </label>
            <input
              value={companyId}
              onChange={(e) => setCompanyId(e.target.value)}
              className="w-full bg-ink border border-line rounded-md p-2.5 text-paper"
            />
          </div>

          <div>
            <label className="block text-xs font-mono uppercase tracking-wider text-muted mb-2">
              Extra context <span className="normal-case text-muted/70">(optional)</span>
            </label>
            <input
              value={extraContext}
              onChange={(e) => setExtraContext(e.target.value)}
              placeholder="e.g. launch campaign for Gen Z audience"
              className="w-full bg-ink border border-line rounded-md p-2.5 text-paper placeholder:text-muted/60"
            />
          </div>

          <button
            type="submit"
            disabled={loading || !isReady()}
            className="mt-2 bg-signal text-ink font-semibold rounded-md py-3 hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {preparingMedia ? "Preparing image…" : loading ? "Simulating…" : "Run impact simulation"}
          </button>

          {error && (
            <p className="text-danger text-sm border border-danger/40 rounded-md p-3">
              {error}
            </p>
          )}
        </form>

        {/* ── Results panel ────────────────────────────────────────── */}
        <div>
          <AnimatePresence mode="wait">
            {!report && !loading && (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="border border-dashed border-line rounded-lg p-10 text-center text-muted h-full flex items-center justify-center"
              >
                Your analysis will appear here.
              </motion.div>
            )}

            {loading && (
              <motion.div
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="border border-line rounded-lg p-10 text-center text-muted"
              >
                <p className="font-mono text-sm">Researching trends and reasoning…</p>
              </motion.div>
            )}

            {report && !loading && (
              <motion.div
                key="report"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex flex-col gap-6"
              >
                <section className="bg-panel border border-line rounded-lg p-6">
                  <h2 className="font-mono text-xs uppercase tracking-wider text-muted mb-3">
                    Predicted trajectory · {report.horizon}
                  </h2>
                  <TrajectoryLine
                    outlook={report.predicted_trajectory.outlook}
                    confidence={report.predicted_trajectory.confidence_score}
                  />
                  <p className="text-paper mt-4">{report.summary}</p>
                  <p className="text-muted text-sm mt-3">
                    {report.predicted_trajectory.reasoning}
                  </p>
                </section>

                {report.perceived_description && (
                  <section className="bg-panel border border-line rounded-lg p-6">
                    <h2 className="font-mono text-xs uppercase tracking-wider text-muted mb-3">
                      What Klyro saw
                    </h2>
                    <p className="text-muted text-sm">{report.perceived_description}</p>
                  </section>
                )}

                {report.trend_signals.length > 0 && (
                  <section className="bg-panel border border-line rounded-lg p-6">
                    <h2 className="font-mono text-xs uppercase tracking-wider text-muted mb-4">
                      Trend signals
                    </h2>
                    <ul className="flex flex-col gap-3">
                      {report.trend_signals.map((t, i) => (
                        <li key={i} className="border-b border-line last:border-0 pb-3 last:pb-0">
                          <div className="flex items-center gap-2">
                            <span
                              className={`w-2 h-2 rounded-full ${
                                t.relevance === "supports"
                                  ? "bg-signal"
                                  : t.relevance === "works_against"
                                  ? "bg-danger"
                                  : "bg-muted"
                              }`}
                            />
                            <span className="font-medium text-paper">{t.trend}</span>
                          </div>
                          <p className="text-muted text-sm mt-1 ml-4">{t.explanation}</p>
                          {t.source_url && (
                            <a
                              href={t.source_url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-signal text-xs font-mono ml-4 inline-block mt-1 hover:underline"
                            >
                              source ↗
                            </a>
                          )}
                        </li>
                      ))}
                    </ul>
                  </section>
                )}

                <div className="grid grid-cols-2 gap-6">
                  <section className="bg-panel border border-line rounded-lg p-6">
                    <h2 className="font-mono text-xs uppercase tracking-wider text-muted mb-4">
                      Risks
                    </h2>
                    <ul className="flex flex-col gap-3">
                      {report.risks.map((r, i) => (
                        <li key={i} className={`border-l-2 pl-3 ${SEVERITY_COLOR[r.severity]}`}>
                          <p className="text-paper text-sm font-medium">{r.label}</p>
                          <p className="text-muted text-xs mt-1">{r.explanation}</p>
                        </li>
                      ))}
                      {report.risks.length === 0 && (
                        <p className="text-muted text-sm">No notable risks found.</p>
                      )}
                    </ul>
                  </section>

                  <section className="bg-panel border border-line rounded-lg p-6">
                    <h2 className="font-mono text-xs uppercase tracking-wider text-muted mb-4">
                      Opportunities
                    </h2>
                    <ul className="flex flex-col gap-3">
                      {report.opportunities.map((o, i) => (
                        <li key={i} className={`border-l-2 pl-3 ${SEVERITY_COLOR[o.severity]}`}>
                          <p className="text-paper text-sm font-medium">{o.label}</p>
                          <p className="text-muted text-xs mt-1">{o.explanation}</p>
                        </li>
                      ))}
                      {report.opportunities.length === 0 && (
                        <p className="text-muted text-sm">None identified.</p>
                      )}
                    </ul>
                  </section>
                </div>

                <section className="bg-panel border border-line rounded-lg p-6">
                  <h2 className="font-mono text-xs uppercase tracking-wider text-muted mb-4">
                    Recommendations
                  </h2>
                  <ol className="flex flex-col gap-2">
                    {report.recommendations.map((r, i) => (
                      <li key={i} className="text-paper text-sm flex gap-3">
                        <span className="font-mono text-signal">{String(i + 1).padStart(2, "0")}</span>
                        {r}
                      </li>
                    ))}
                  </ol>
                </section>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
