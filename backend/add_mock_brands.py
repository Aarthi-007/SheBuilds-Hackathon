import asyncio
from app.database import init_db
from app.models.user import User, Organization
from app.models.brand import Brand, BrandAsset
from app.models.identity import BrandIdentity
from app.models.campaign import Campaign, CampaignVersion
from app.models.validation import ValidationReport
from app.models.trend import TrendReport
from app.utils.security import get_password_hash

MOCK_BRANDS = [
    {
        "name": "Nike Athletic",
        "industry": "Sports & Apparel",
        "website": "https://nike.com",
        "description": "Empowering athletes everywhere with innovation, performance gear, and motivational storytelling.",
        "languages": ["English"],
        "asset": {
            "name": "Nike Air Max 2026 Campaign Guidelines",
            "type": "pdf",
            "category": "Brand Guidelines",
            "path": "/storage/brands/nike/guidelines.pdf",
            "url": "http://localhost:8000/storage/brands/nike/guidelines.pdf",
            "size": 512000,
            "mime": "application/pdf",
            "metadata": {"pages": 32, "language": "English"}
        },
        "identity": {
            "voice": {
                "archetype": "The Hero & Achiever",
                "tone": "Bold, Motivational, Direct, High-Energy",
                "keywords": ["Empowerment", "Athletic", "Relentless", "Speed", "Innovation"],
                "rules": [
                    "Use active, punchy sentences.",
                    "Emphasize perseverance, triumph over limits, and peak performance.",
                    "Avoid passive or apologetic wording."
                ]
            },
            "visual": {
                "color_palette": ["#000000", "#FF4500", "#FFFFFF", "#111111"],
                "typography": ["Futura Bold", "Helvetica Neue", "Arial Black"],
                "logo_placement": "Top Left / Center Clear Space",
                "image_style": "High-contrast dynamic motion photography of athletes in action."
            },
            "emotion": {
                "primary": "Determination & Inspiration",
                "target_feeling": "Empowered to push past personal limits and achieve greatness.",
                "tone_curve": "Starts with obstacle -> Builds tension -> Culminates in triumphant breakthrough."
            },
            "audience": {
                "primary_demographic": "Athletes, Fitness Enthusiasts & Gen Z/Millennials (Ages 16-38)",
                "psychographics": "Goal-driven, competitive, active lifestyle seekers.",
                "core_desires": "Peak athletic performance, self-improvement, stylish street performance gear."
            },
            "keywords": ["JustDoIt", "PeakPerformance", "AirMax2026", "RunUnstoppable", "Limitless"],
            "personality": ["Empowering", "Fearless", "Pioneering", "High-Energy"],
            "design_rules": [
                "Always maintain clean stark dark backgrounds for high contrast visuals.",
                "Incorporate movement blur or action dynamic angles in featured imagery."
            ],
            "brand_summary": "Nike Athletic focuses on high-impact motivational storytelling, stark minimalist visuals, and unrelenting athletic empowerment.",
            "confidence_score": 0.98,
            "status": "ready"
        },
        "campaign": {
            "title": "Unstoppable Speed 2026",
            "description": "Global summer launch for the Air Max Speed line focusing on urban runners.",
            "platform": "Instagram & TikTok",
            "objective": "High Velocity Engagement & Direct Conversions",
            "version": {
                "text_content": "Break your limits before the clock starts. The new Air Max Speed is engineered for relentless pursuit. Just Do It.",
                "generated_by": "AI Engine",
                "validation_score": 97.8,
                "approved": True
            },
            "validation": {
                "overall_score": 97.8,
                "status": "approved",
                "scores": {"identity": 99.0, "visual": 97.0, "compliance": 100.0, "copyright": 95.0, "safety": 99.0, "context": 97.0},
                "issues": [],
                "recommendations": ["Certified for global multi-channel ad execution."]
            }
        },
        "trend": {
            "trend": "Urban Night Running Communities",
            "category": "Fitness & Lifestyle",
            "alignment_score": 98.0,
            "trend_score": 95.5,
            "competition_score": 72.0,
            "forecast_score": 97.0,
            "recommended_platform": "TikTok & Instagram Reels",
            "best_posting_time": "21:00",
            "generated_campaign": {
                "title": "Nike - Own the Night Run",
                "caption": "When the city sleeps, the runners take over. Light up the night in high-visibility reflective gear. #JustDoIt"
            },
            "hashtags": ["#NightRunners", "#AirMaxSpeed", "#JustDoIt", "#UrbanAthletes"],
            "status": "recommended"
        }
    },
    {
        "name": "Klyros Eco Energy",
        "industry": "Clean Technology & Energy",
        "website": "https://klyros-eco.io",
        "description": "Next-generation intelligent solar and microgrid solutions powering sustainable smart homes.",
        "languages": ["English"],
        "asset": {
            "name": "Klyros Eco Smart Grid Whitepaper 2026",
            "type": "pdf",
            "category": "Technical Overview",
            "path": "/storage/brands/klyros_eco/whitepaper.pdf",
            "url": "http://localhost:8000/storage/brands/klyros_eco/whitepaper.pdf",
            "size": 340000,
            "mime": "application/pdf",
            "metadata": {"pages": 18, "language": "English"}
        },
        "identity": {
            "voice": {
                "archetype": "The Visionary & Sage",
                "tone": "Forward-Looking, Precise, Inspiring, Environmentally Conscious",
                "keywords": ["Sustainability", "CleanTech", "SmartEnergy", "ZeroCarbon", "Autonomy"],
                "rules": [
                    "Focus on eco-impact metrics and smart efficiency.",
                    "Use hopeful, technology-forward language.",
                    "Avoid alarmist or pessimistic environmental doom-mongering."
                ]
            },
            "visual": {
                "color_palette": ["#0F4C81", "#00C897", "#E0F7FA", "#FFFFFF"],
                "typography": ["Inter", "SF Pro Display", "Roboto"],
                "logo_placement": "Top Right Clean Corner",
                "image_style": "Bright, airy modern architectural render showcasing integrated solar glass & green roofs."
            },
            "emotion": {
                "primary": "Optimism & Empowerment",
                "target_feeling": "Confidence in a sustainable, self-sufficient energy future.",
                "tone_curve": "Educational insight -> Environmental impact proof -> Empowered action."
            },
            "audience": {
                "primary_demographic": "Eco-Conscious Homeowners & Tech Innovators (Ages 28-55)",
                "psychographics": "Environmentally driven, early tech adopters, efficiency focused.",
                "core_desires": "Energy independence, lower utility bills, reduced carbon footprint."
            },
            "keywords": ["ZeroCarbon", "CleanEnergy", "SmartGrid", "SolarIntelligence", "EcoPower"],
            "personality": ["Visionary", "Trustworthy", "Innovative", "Eco-Centric"],
            "design_rules": [
                "Emphasize clean teal and deep emerald green accents.",
                "Feature sleek UI dashboards showing real-time solar generation."
            ],
            "brand_summary": "Klyros Eco Energy combines cutting-edge AI smart grid technology with sleek green aesthetics to power sustainable independence.",
            "confidence_score": 0.95,
            "status": "ready"
        },
        "campaign": {
            "title": "Power Your Independence",
            "description": "Earth Day launch campaign for the Klyros Home Microgrid AI system.",
            "platform": "LinkedIn & Instagram",
            "objective": "Lead Generation & Thought Leadership",
            "version": {
                "text_content": "Take full control of your home's energy future. Klyros Smart Microgrids store 40% more solar energy automatically.",
                "generated_by": "AI Engine",
                "validation_score": 96.2,
                "approved": True
            },
            "validation": {
                "overall_score": 96.2,
                "status": "approved",
                "scores": {"identity": 97.0, "visual": 96.0, "compliance": 98.0, "copyright": 94.0, "safety": 98.0, "context": 95.0},
                "issues": [],
                "recommendations": ["Highlight energy storage statistics in visual carousel."]
            }
        },
        "trend": {
            "trend": "AI-Driven Home Efficiency",
            "category": "Smart Home Tech",
            "alignment_score": 97.0,
            "trend_score": 93.0,
            "competition_score": 60.0,
            "forecast_score": 96.0,
            "recommended_platform": "LinkedIn & YouTube",
            "best_posting_time": "10:00",
            "generated_campaign": {
                "title": "Klyros - The Intelligent Clean Home",
                "caption": "Why let peak rate pricing drain your budget? Let AI optimize your home energy grid automatically. #CleanEnergy"
            },
            "hashtags": ["#CleanEnergy", "#SmartHome", "#Sustainability", "#KlyrosEco"],
            "status": "recommended"
        }
    }
]

async def seed_additional_brands():
    print("--- Adding Mock Brands into Database ---")
    await init_db()

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

    for item in MOCK_BRANDS:
        brand = await Brand.find_one({"name": item["name"]})
        if not brand:
            brand = Brand(
                organization_id=str(org.id),
                name=item["name"],
                industry=item["industry"],
                website=item["website"],
                description=item["description"],
                languages=item["languages"],
                created_by=str(user.id)
            )
            await brand.insert()
            print(f"  [Created Brand] {brand.name} (ID: {brand.id})")

        # Asset
        asset = await BrandAsset.find_one({"brand_id": str(brand.id)})
        if not asset:
            a_data = item["asset"]
            asset = BrandAsset(
                brand_id=str(brand.id),
                asset_name=a_data["name"],
                asset_type=a_data["type"],
                category=a_data["category"],
                storage_path=a_data["path"],
                storage_url=a_data["url"],
                file_size=a_data["size"],
                mime_type=a_data["mime"],
                processing_status="completed",
                metadata=a_data["metadata"]
            )
            await asset.insert()
            print(f"  [Created Asset] {asset.asset_name}")

        # Identity
        identity = await BrandIdentity.find_one({"brand_id": str(brand.id)})
        if not identity:
            id_data = item["identity"]
            identity = BrandIdentity(
                brand_id=str(brand.id),
                version=1,
                voice=id_data["voice"],
                visual=id_data["visual"],
                emotion=id_data["emotion"],
                audience=id_data["audience"],
                keywords=id_data["keywords"],
                personality=id_data["personality"],
                design_rules=id_data["design_rules"],
                brand_summary=id_data["brand_summary"],
                confidence_score=id_data["confidence_score"],
                status=id_data["status"],
                assets_processed_count=1
            )
            await identity.insert()
            print(f"  [Created Identity] {brand.name} Identity Model")

        # Campaign
        campaign = await Campaign.find_one({"brand_id": str(brand.id)})
        if not campaign:
            c_data = item["campaign"]
            campaign = Campaign(
                brand_id=str(brand.id),
                title=c_data["title"],
                description=c_data["description"],
                platform=c_data["platform"],
                objective=c_data["objective"],
                status="certified",
                current_version=1,
                created_by=str(user.id)
            )
            await campaign.insert()

            v_data = c_data["version"]
            version = CampaignVersion(
                campaign_id=str(campaign.id),
                version=1,
                text_content=v_data["text_content"],
                generated_by=v_data["generated_by"],
                validation_score=v_data["validation_score"],
                approved=v_data["approved"]
            )
            await version.insert()

            val_data = c_data["validation"]
            val_report = ValidationReport(
                campaign_id=str(campaign.id),
                campaign_version_id=str(version.id),
                brand_id=str(brand.id),
                overall_score=val_data["overall_score"],
                status=val_data["status"],
                scores=val_data["scores"],
                issues=val_data["issues"],
                recommendations=val_data["recommendations"]
            )
            await val_report.insert()
            print(f"  [Created Campaign & Validation] {campaign.title}")

        # Trend
        trend = await TrendReport.find_one({"brand_id": str(brand.id)})
        if not trend:
            t_data = item["trend"]
            trend = TrendReport(
                brand_id=str(brand.id),
                trend=t_data["trend"],
                category=t_data["category"],
                alignment_score=t_data["alignment_score"],
                trend_score=t_data["trend_score"],
                competition_score=t_data["competition_score"],
                forecast_score=t_data["forecast_score"],
                recommended_platform=t_data["recommended_platform"],
                best_posting_time=t_data["best_posting_time"],
                generated_campaign=t_data["generated_campaign"],
                hashtags=t_data["hashtags"],
                status=t_data["status"]
            )
            await trend.insert()
            print(f"  [Created Trend Report] {trend.trend}")

    print("\n--- Mock Brands Successfully Added to Database! ---")

if __name__ == "__main__":
    asyncio.run(seed_additional_brands())
