"use client";

import { useState, useEffect } from "react";
import { Loader2, Fingerprint, Activity, Tag, Users, CheckCircle, RefreshCw, Layers } from "lucide-react";
import { clsx } from "clsx";
import { API_BASE, buildHeaders } from "@/lib/api";

interface BrandIdentityData {
  voice?: Record<string, unknown> | string;
  visual?: Record<string, unknown> | string;
  emotion?: Record<string, unknown> | string;
  audience?: Record<string, unknown> | string;
  keywords?: string[];
  personality?: string[] | string;
  design_rules?: string[] | string;
  brand_summary?: string;
  confidence_score?: number;
}

export function BrandIdentityView({ brandId }: { brandId?: string }) {
  const [identity, setIdentity] = useState<BrandIdentityData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRebuilding, setIsRebuilding] = useState(false);
  const [error, setError] = useState("");

  const targetBrandId = brandId || "latest";

  // Format Voice & Tone
  const formatVoice = (v: any) => {
    if (!v) return "Awaiting asset analysis for voice synthesis.";
    if (typeof v === "string") return v;
    const tone = v.tone || v.voice || v.style;
    const style = v.style || v.reading_level || v.cta_style;
    if (tone && style && tone !== style) return `${tone} (${style})`;
    return tone || style || "Conversational & Authentic";
  };

  // Format Visual Aesthetic
  const formatVisual = (v: any) => {
    if (!v) return "Awaiting asset analysis for visual synthesis.";
    if (typeof v === "string") return v;
    
    const parts = [];
    if (v.primary_colors && Array.isArray(v.primary_colors) && v.primary_colors.length > 0) {
      parts.push(`Colors: ${v.primary_colors.join(", ")}`);
    }
    if (v.logo_position) parts.push(`Logo: ${v.logo_position}`);
    if (v.layout) parts.push(`Layout: ${v.layout}`);
    if (v.typography) parts.push(`Typography: ${v.typography}`);

    if (parts.length > 0) return parts.join(" | ");
    return "Clean & Modern Visual Aesthetics";
  };

  // Format Emotional Core
  const formatEmotion = (e: any) => {
    if (!e) return "Awaiting asset analysis for emotional core.";
    if (typeof e === "string") return e;
    if (typeof e === "object" && Object.keys(e).length > 0) {
      const items = Object.entries(e).map(([k, v]) => `${k.charAt(0).toUpperCase() + k.slice(1)}: ${v}%`);
      if (items.length > 0) return items.join(", ");
    }
    return "Trust & Engagement";
  };

  // Format Target Audience
  const formatAudience = (a: any) => {
    if (!a) return "Awaiting asset analysis for target audience.";
    if (typeof a === "string") return a;
    if (typeof a === "object" && Object.keys(a).length > 0) {
      return a.primary || a.secondary || Object.values(a).join(", ");
    }
    return "Target Consumers & Professionals";
  };

  const safeList = (field: string[] | string | undefined): string[] => {
    if (!field) return [];
    if (Array.isArray(field)) return field;
    return [field];
  };

  useEffect(() => {
    fetchIdentity();
  }, [targetBrandId]);

  const fetchIdentity = async () => {
    setIsLoading(true);
    setError("");
    try {
      const response = await fetch(`${API_BASE}/identity/${targetBrandId}`, {
        headers: buildHeaders()
      });
      if (response.ok) {
        const result = await response.json();
        if (result.success && result.data) {
          setIdentity(result.data);
        } else {
          setIdentity(null);
          setError(result.message || "Unable to load brand identity.");
        }
      } else {
        const result = await response.json();
        setError(result.detail || "Unable to load brand identity.");
        setIdentity(null);
      }
    } catch (err) {
      console.error(err);
      setError("Network error while fetching brand identity.");
      setIdentity(null);
    } finally {
      setIsLoading(false);
    }
  };

  const rebuildIdentity = async () => {
    setIsRebuilding(true);
    setError("");
    try {
      const response = await fetch(`${API_BASE}/identity/build/${targetBrandId}?force_rebuild=true`, {
        method: "POST",
        headers: buildHeaders()
      });
      const result = await response.json();
      if (response.ok && result.success && result.data && result.data.identity) {
        setIdentity(result.data.identity);
      } else {
        setError(result.message || "Failed to rebuild brand identity.");
      }
    } catch (err) {
      console.error(err);
      setError("Network error when rebuilding brand identity.");
    } finally {
      setIsRebuilding(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh]">
        <Loader2 className="w-8 h-8 text-primary-500 animate-spin mb-4" />
        <p className="text-slate-500 font-medium">Loading Brand Identity Matrix...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 text-red-700 p-4 rounded-xl border border-red-100 flex items-center gap-3">
        <Activity className="w-5 h-5 text-red-500" />
        <p className="font-medium text-sm">{error}</p>
        <button onClick={fetchIdentity} className="ml-auto underline text-sm hover:text-red-900">Retry</button>
      </div>
    );
  }

  if (!identity) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] text-center px-4">
        <div className="w-16 h-16 bg-primary-50 text-primary-600 flex items-center justify-center rounded-full mb-4">
          <Fingerprint className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold text-slate-800 mb-2">No Identity Model Found</h2>
        <p className="text-slate-500 max-w-md mb-6">
          Your brand's neural identity has not been generated yet. Klyro needs to analyze your assets and onboarding inputs to synthesize your core matrix.
        </p>
        <button 
          onClick={rebuildIdentity}
          disabled={isRebuilding}
          className="btn-primary flex items-center gap-2"
        >
          {isRebuilding ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
          Synthesize Identity Model
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Fingerprint className="w-6 h-6 text-primary-600" />
            Brand Identity Matrix
          </h1>
          <p className="text-sm text-slate-500 mt-1">AI-synthesized representation of your core brand DNA.</p>
        </div>
        
        <button 
          onClick={rebuildIdentity}
          disabled={isRebuilding}
          className="flex items-center justify-center gap-2 px-4 py-2 bg-white border border-slate-200 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-50 hover:text-primary-600 transition-colors shadow-sm"
        >
          {isRebuilding ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <RefreshCw className="w-4 h-4" />
          )}
          Re-Analyze & Evolve Brand
        </button>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-card p-6 md:col-span-2 bg-gradient-to-br from-primary-600 to-indigo-700 text-white relative overflow-hidden">
          <div className="relative z-10">
            <h3 className="text-lg font-semibold text-primary-50 flex items-center gap-2 mb-2">
              <Activity className="w-5 h-5 text-emerald-400" />
              Executive Summary
            </h3>
            <p className="text-sm text-primary-100 leading-relaxed font-medium">
              {identity.brand_summary || "Brand Identity Model dynamically synthesized from FeatureStore evidence records."}
            </p>
          </div>
          <Fingerprint className="absolute -bottom-8 -right-8 w-48 h-48 text-white opacity-5" />
        </div>

        <div className="glass-card p-6 flex flex-col justify-center items-center text-center bg-white border-b-4 border-b-emerald-500">
          <p className="text-sm font-medium text-slate-500 mb-1">AI Confidence Score</p>
          <div className="flex items-baseline gap-1">
            <span className="text-4xl font-extrabold text-slate-800">{identity.confidence_score ? Math.round(identity.confidence_score > 1 ? identity.confidence_score : identity.confidence_score * 100) : 95}</span>
            <span className="text-lg font-semibold text-slate-400">%</span>
          </div>
          <p className="text-xs text-emerald-600 font-medium flex items-center gap-1 mt-2 bg-emerald-50 px-2.5 py-1 rounded-full">
            <CheckCircle className="w-3.5 h-3.5" /> High Alignment
          </p>
        </div>
      </div>

      {/* Core Matrix Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        <div className="glass-card p-6 border-l-4 border-l-primary-500">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-primary-50 flex items-center justify-center">
              <Activity className="w-4 h-4 text-primary-600" />
            </div>
            <h3 className="text-md font-bold text-slate-800">Brand Voice & Tone</h3>
          </div>
          <p className="text-sm text-slate-600 leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-100">
            {formatVoice(identity.voice)}
          </p>
        </div>

        <div className="glass-card p-6 border-l-4 border-l-indigo-500">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-indigo-50 flex items-center justify-center">
              <Layers className="w-4 h-4 text-indigo-600" />
            </div>
            <h3 className="text-md font-bold text-slate-800">Visual Aesthetic</h3>
          </div>
          <div className="text-sm text-slate-600 leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-100">
            {formatVisual(identity.visual)}
          </div>
        </div>

        <div className="glass-card p-6 border-l-4 border-l-pink-500">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-pink-50 flex items-center justify-center">
              <Tag className="w-4 h-4 text-pink-600" />
            </div>
            <h3 className="text-md font-bold text-slate-800">Emotional Core</h3>
          </div>
          <p className="text-sm text-slate-600 leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-100">
            {formatEmotion(identity.emotion)}
          </p>
        </div>

        <div className="glass-card p-6 border-l-4 border-l-amber-500">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-amber-50 flex items-center justify-center">
              <Users className="w-4 h-4 text-amber-600" />
            </div>
            <h3 className="text-md font-bold text-slate-800">Target Audience</h3>
          </div>
          <p className="text-sm text-slate-600 leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-100">
            {formatAudience(identity.audience)}
          </p>
        </div>

      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-card p-6">
          <h3 className="text-md font-bold text-slate-800 mb-4 flex items-center gap-2">
            <Tag className="w-4 h-4 text-slate-400" />
            Core Keywords
          </h3>
          <div className="flex flex-wrap gap-2">
            {safeList(identity.keywords).length > 0 ? (
              safeList(identity.keywords).map((kw, i) => (
                <span key={i} className="px-3 py-1 bg-white border border-slate-200 text-slate-700 text-xs font-medium rounded-full shadow-sm">
                  {kw}
                </span>
              ))
            ) : (
              <span className="text-xs text-slate-400">No keywords synthesized yet.</span>
            )}
          </div>
        </div>
        
        <div className="glass-card p-6">
           <h3 className="text-md font-bold text-slate-800 mb-4 flex items-center gap-2">
            <Activity className="w-4 h-4 text-slate-400" />
            Design Rules
          </h3>
          <div className="text-sm text-slate-600 leading-relaxed">
            {safeList(identity.design_rules).length > 0 ? (
              <ul className="list-disc list-inside space-y-1">
                {safeList(identity.design_rules).map((rule, idx) => (
                  <li key={idx}>{rule}</li>
                ))}
              </ul>
            ) : (
              <p className="text-xs text-slate-400">No design rules synthesized yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
