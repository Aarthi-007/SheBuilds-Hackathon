import asyncio
from app.database import init_db
from app.models.user import User, Organization
from app.models.brand import Brand, BrandAsset
from app.models.identity import BrandIdentity, AIMemory
from app.models.campaign import Campaign, CampaignVersion
from app.models.validation import ValidationReport
from app.models.trend import TrendReport
from app.utils.security import get_password_hash
from app.ai.multimodal_analyzer import MultimodalAnalyzer

async def seed_data():
    print("--- Initializing Database for Seeding ---")
    await init_db()

    # Seed Organization
    org = await Organization.find_one({"slug": "amul"})
    if not org:
        org = Organization(
            name="Amul Dairy Cooperative",
            slug="amul",
            industry="Food & Dairy",
            plan="Enterprise"
        )
        await org.insert()
        print("  [Seeded] Organization: Amul Dairy Cooperative")

    # Seed User
    user = await User.find_one({"email": "rahul@amul.com"})
    if not user:
        user = User(
            organization_id=str(org.id),
            full_name="Rahul Kumar",
            email="rahul@amul.com",
            password_hash=get_password_hash("Password@123"),
            role="brand_manager"
        )
        await user.insert()
        print("  [Seeded] User: rahul@amul.com (Password: Password@123)")

    # Seed Brand
    brand = await Brand.find_one({"name": "Amul"})
    if not brand:
        brand = Brand(
            organization_id=str(org.id),
            name="Amul",
            industry="Food & Dairy",
            website="https://amul.com",
            description="The Taste of India - India's leading dairy brand",
            languages=["English", "Hindi"],
            created_by=str(user.id)
        )
        await brand.insert()
        print("  [Seeded] Brand: Amul")

    # Seed Asset
    asset = await BrandAsset.find_one({"brand_id": str(brand.id)})
    if not asset:
        asset = BrandAsset(
            brand_id=str(brand.id),
            asset_name="Amul Butter Campaign Guidelines",
            asset_type="pdf",
            category="Brand Guidelines",
            storage_path="/storage/brands/amul/guidelines.pdf",
            storage_url="http://localhost:8000/storage/brands/amul/guidelines.pdf",
            file_size=204800,
            mime_type="application/pdf",
            processing_status="completed",
            metadata={"pages": 24, "language": "English"}
        )
        await asset.insert()
        print("  [Seeded] Brand Asset")

    # Seed Brand Identity
    identity = await BrandIdentity.find_one({"brand_id": str(brand.id)})
    if not identity:
        analysis = MultimodalAnalyzer.build_brand_identity("Amul", [{"asset_type": "pdf"}])
        identity = BrandIdentity(
            brand_id=str(brand.id),
            version=1,
            voice=analysis["voice"],
            visual=analysis["visual"],
            emotion=analysis["emotion"],
            audience=analysis["audience"],
            keywords=analysis["keywords"],
            personality=analysis["personality"],
            design_rules=analysis["design_rules"],
            brand_summary=analysis["brand_summary"],
            confidence_score=0.96,
            status="ready",
            assets_processed_count=1
        )
        await identity.insert()
        print("  [Seeded] Brand Identity Model")

    # Seed Campaign
    campaign = await Campaign.find_one({"brand_id": str(brand.id)})
    if not campaign:
        campaign = Campaign(
            brand_id=str(brand.id),
            title="Diwali Family Celebration",
            description="Warm family celebration featuring Amul Butter & Sweets",
            platform="Instagram",
            objective="Brand Engagement",
            status="certified",
            current_version=1,
            created_by=str(user.id)
        )
        await campaign.insert()

        version = CampaignVersion(
            campaign_id=str(campaign.id),
            version=1,
            text_content="Bring home the trusted taste and quality that every family loves together!",
            generated_by="AI Engine",
            validation_score=96.5,
            approved=True
        )
        await version.insert()
        print("  [Seeded] Campaign & Version")

        val_report = ValidationReport(
            campaign_id=str(campaign.id),
            campaign_version_id=str(version.id),
            brand_id=str(brand.id),
            overall_score=96.5,
            status="approved",
            scores={"identity": 98.0, "visual": 95.0, "compliance": 100.0, "copyright": 94.0, "safety": 98.0, "context": 95.0},
            issues=[],
            recommendations=["Campaign optimization certified with 96.5% score."]
        )
        await val_report.insert()
        print("  [Seeded] Validation Report")

    # Seed Trend
    trend = await TrendReport.find_one({"brand_id": str(brand.id)})
    if not trend:
        trend = TrendReport(
            brand_id=str(brand.id),
            trend="Cricket World Cup Season",
            category="Sports & Celebration",
            alignment_score=96.5,
            trend_score=94.0,
            competition_score=68.0,
            forecast_score=95.0,
            recommended_platform="Instagram",
            best_posting_time="19:00",
            generated_campaign={
                "title": "Amul - Celebrating Every Victory Together",
                "caption": "Every win feels sweeter when shared with family! Enjoy every match with Amul."
            },
            hashtags=["#CricketFever", "#AmulCelebrates", "#TogetherInVictory"],
            status="recommended"
        )
        await trend.insert()
        print("  [Seeded] Trend Report")

    print("\n--- Seed Data Completed Successfully! ---")

if __name__ == "__main__":
    asyncio.run(seed_data())
