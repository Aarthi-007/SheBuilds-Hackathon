import { motion } from "framer-motion";
import type { Outlook } from "../../lib/types";

const OUTLOOK_META: Record<Outlook, { color: string; path: string; label: string }> = {
  improving: {
    color: "#5CE1B0",
    path: "M0,70 C60,68 100,55 150,45 C220,32 260,20 320,10",
    label: "trending up",
  },
  stable: {
    color: "#8A8DA3",
    path: "M0,45 C60,42 100,48 150,44 C220,40 260,46 320,42",
    label: "holding steady",
  },
  declining: {
    color: "#E85D5D",
    path: "M0,15 C60,20 100,35 150,45 C220,58 260,68 320,78",
    label: "trending down",
  },
  volatile: {
    color: "#F2A93B",
    path: "M0,45 C40,15 80,75 120,30 C160,70 200,15 240,60 C270,30 300,55 320,40",
    label: "swinging both ways",
  },
};

export default function TrajectoryLine({
  outlook,
  confidence,
}: {
  outlook: Outlook;
  confidence: number;
}) {
  const meta = OUTLOOK_META[outlook];

  return (
    <div className="relative">
      <svg viewBox="0 0 320 90" className="w-full h-24" preserveAspectRatio="none">
        {/* baseline grid */}
        <line x1="0" y1="45" x2="320" y2="45" stroke="#2A2D3A" strokeWidth="1" strokeDasharray="2 4" />
        <motion.path
          d={meta.path}
          fill="none"
          stroke={meta.color}
          strokeWidth="2.5"
          strokeLinecap="round"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 1 }}
          transition={{ duration: 1.1, ease: "easeInOut" }}
        />
      </svg>
      <div className="flex items-center justify-between mt-2">
        <span className="font-mono text-xs uppercase tracking-wider" style={{ color: meta.color }}>
          {outlook} · {meta.label}
        </span>
        <span className="font-mono text-xs text-muted">
          confidence {Math.round(confidence * 100)}%
        </span>
      </div>
    </div>
  );
}
