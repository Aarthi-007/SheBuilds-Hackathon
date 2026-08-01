import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(__file__))

from app.main import app

def run_e2e_tests():
    print("--- Running Klyros Backend End-to-End Test Suite ---")
    with TestClient(app) as client:
        # 1. Health check
        res = client.get("/")
        assert res.status_code == 200
        print("  [Pass] 1. Root / Health Check")

        # 2. Register
        reg_payload = {
            "organization_name": "Klyros Enterprise",
            "full_name": "Test Manager",
            "email": "testmanager@klyros.com",
            "password": "Password@123"
        }
        res = client.post("/api/v1/auth/register", json=reg_payload)
        if res.status_code != 200:
            res = client.post("/api/v1/auth/login", json={"email": reg_payload["email"], "password": reg_payload["password"]})
        
        assert res.status_code == 200
        token_data = res.json()["data"]
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        print("  [Pass] 2. Authentication & JWT Token Acquisition")

        # 3. Create Brand
        brand_payload = {
            "name": "Klyros Audio",
            "industry": "Consumer Electronics",
            "website": "https://klyrosaudio.com",
            "description": "Premium sound for modern creators",
            "languages": ["English"]
        }
        res = client.post("/api/v1/brands", json=brand_payload, headers=headers)
        assert res.status_code == 200
        brand = res.json()["data"]
        brand_id = brand["id"]
        print(f"  [Pass] 3. Brand Created: {brand['name']} (ID: {brand_id})")

        # 4. Upload Brand Asset
        mock_file = ("brand_logo.png", b"fake image bytes content", "image/png")
        res = client.post(f"/api/v1/brands/{brand_id}/assets", files={"files": mock_file}, data={"category": "Logo"}, headers=headers)
        assert res.status_code == 200
        assets_data = res.json()["data"]
        job_id = assets_data["job_id"]
        print(f"  [Pass] 4. Asset Uploaded & Job Triggered (Job ID: {job_id})")

        # 5. Build Brand Identity Model
        res = client.post(f"/api/v1/identity/build/{brand_id}", headers=headers)
        assert res.status_code == 200
        identity = res.json()["data"]["identity"]
        assert identity["status"] == "ready"
        print(f"  [Pass] 5. Brand Identity Model Synthesized (Voice: {identity['voice']['tone']})")

        # 6. Validate AI Campaign Content
        val_payload = {
            "brand_id": brand_id,
            "text_content": "Experience sound crafted with family trust and innovation.",
            "platform": "Instagram"
        }
        res = client.post("/api/v1/validation/check", json=val_payload, headers=headers)
        assert res.status_code == 200
        val_report = res.json()["data"]
        print(f"  [Pass] 6. 6-Pillar Brand Validation Certification (Score: {val_report['overall_score']}%)")

        # 7. Create Campaign & Run AI Optimization
        camp_payload = {
            "brand_id": brand_id,
            "title": "Unmatched Clarity Campaign",
            "description": "Highlighting crisp audio quality",
            "platform": "Instagram",
            "text_content": "Try our new headphones now."
        }
        res = client.post("/api/v1/campaigns", json=camp_payload, headers=headers)
        assert res.status_code == 200
        campaign_id = res.json()["data"]["campaign"]["id"]

        opt_payload = {"campaign_id": campaign_id}
        res = client.post("/api/v1/optimization/run", json=opt_payload, headers=headers)
        assert res.status_code == 200
        opt_report = res.json()["data"]["report"]
        print(f"  [Pass] 7. Closed-Loop AI Content Optimization (Score Before: {opt_report['validation_score_before']}%, After: {opt_report['validation_score_after']}%)")

        # 8. Discover Market Trends & Align
        trend_payload = {"brand_id": brand_id}
        res = client.post("/api/v1/trends/discover", json=trend_payload, headers=headers)
        assert res.status_code == 200
        trends = res.json()["data"]
        print(f"  [Pass] 8. Brand Trend Intelligence Engine (Top Trend: {trends[0]['trend']}, Alignment: {trends[0]['alignment_score']}%)")

        # 9. AI Memory Storage & Retrieval
        mem_payload = {
            "brand_id": brand_id,
            "entity_type": "campaign",
            "entity_id": campaign_id,
            "content_text": "Premium sound for modern creators",
            "summary": "Audio campaign memory"
        }
        res = client.post("/api/v1/memory/store", json=mem_payload, headers=headers)
        assert res.status_code == 200
        print("  [Pass] 9. AI Semantic Memory Stored")

        # 10. Dashboard Stats
        res = client.get("/api/v1/dashboard", headers=headers)
        assert res.status_code == 200
        dash_data = res.json()["data"]
        print(f"  [Pass] 10. Dashboard & Analytics Consolidated (Total Brands: {dash_data['total_brands']}, Campaigns: {dash_data['total_campaigns']})")

    print("\n--- All 10 Klyros Backend Modules Passed Verification! ---")

def test_e2e_flow():
    run_e2e_tests()


if __name__ == "__main__":
    test_e2e_flow()
