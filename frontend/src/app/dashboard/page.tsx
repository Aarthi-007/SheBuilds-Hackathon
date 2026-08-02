"use client";

import { useState, useEffect } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopNav } from "@/components/layout/TopNav";
import { OverviewView } from "@/components/dashboard/OverviewView";
import { AssetIngestionView } from "@/components/dashboard/AssetIngestionView";
import { BrandIdentityView } from "@/components/dashboard/BrandIdentityView";
import { ValidationView } from "@/components/dashboard/ValidationView";
import { TrendAnalyticsView } from "@/components/dashboard/TrendAnalyticsView";
import { ImpactSimulationView } from "@/components/dashboard/ImpactSimulationView";
import { SettingsView } from "@/components/dashboard/SettingsView";
import { CopilotView } from "@/components/dashboard/CopilotView";
import { API_BASE, buildHeaders } from "@/lib/api";

export default function DashboardClient() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [brands, setBrands] = useState<Array<{ id: string; name: string }>>([]);
  const [activeBrandId, setActiveBrandId] = useState<string>("");

  useEffect(() => {
    fetchBrands();
  }, []);

  const fetchBrands = async () => {
    try {
      const res = await fetch(`${API_BASE}/brands`, {
        headers: buildHeaders()
      });
      if (res.ok) {
        const result = await res.json();
        if (result.success && Array.isArray(result.data) && result.data.length > 0) {
          setBrands(result.data);
          const savedId = localStorage.getItem("active_brand_id");
          if (savedId && result.data.some((b: any) => b.id === savedId)) {
            setActiveBrandId(savedId);
          } else {
            const latestId = result.data[result.data.length - 1].id;
            setActiveBrandId(latestId);
            localStorage.setItem("active_brand_id", latestId);
          }
        }
      }
    } catch (e) {
      console.error("Failed to fetch brands", e);
    }
  };

  const handleSelectBrand = (id: string) => {
    setActiveBrandId(id);
    localStorage.setItem("active_brand_id", id);
  };

  const renderView = () => {
    switch (activeTab) {
      case "dashboard":
        return <OverviewView setActiveTab={setActiveTab} brandId={activeBrandId} />;
      case "assets":
        return <AssetIngestionView brandId={activeBrandId} onBrandCreated={fetchBrands} />;
      case "identity":
        return <BrandIdentityView brandId={activeBrandId} />;
      case "validation":
        return <ValidationView brandId={activeBrandId} />;
      case "trends":
        return <TrendAnalyticsView brandId={activeBrandId} />;
      case "simulation":
        return <ImpactSimulationView brandId={activeBrandId} />;
      case "copilot":
        return <CopilotView brandId={activeBrandId} />;
      case "settings":
        return <SettingsView />;
      default:
        return <OverviewView setActiveTab={setActiveTab} brandId={activeBrandId} />;
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        isOpen={isMobileMenuOpen} 
        setIsOpen={setIsMobileMenuOpen} 
      />
      <div className="flex-1 flex flex-col min-w-0">
        <TopNav 
          onMenuToggle={() => setIsMobileMenuOpen(!isMobileMenuOpen)} 
          brands={brands}
          activeBrandId={activeBrandId}
          onSelectBrand={handleSelectBrand}
        />
        <main className="flex-1 p-4 lg:p-8 overflow-y-auto">
          <div className="mx-auto max-w-7xl">
            {renderView()}
          </div>
        </main>
      </div>
    </div>
  );
}
