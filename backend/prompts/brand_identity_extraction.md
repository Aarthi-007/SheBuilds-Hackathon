You are a brand strategist. Analyze the following batch of content from company "{{company_id}}" and extract a comprehensive brand identity profile.

Content batch:
{{content_batch}}

Extract and return a JSON object with exactly these keys matching the BrandIdentityModel schema:
- "company_id": "{{company_id}}"
- "industry": detected industry (string)
- "tone": list of tone descriptors (e.g., ["professional", "witty", "warm"])
- "core_values": list of brand values (e.g., ["sustainability", "innovation"])
- "personality_traits": list of personality traits (e.g., ["bold", "approachable"])
- "messaging_pillars": list of key messaging themes (e.g., ["customer-first", "quality craftsmanship"])
- "target_audience": object with keys "primary_segment", "age_range", "psychographics", "pain_points"
- "visual_identity": object with keys "colors", "typography_style", "logo_usage_rules", "imagery_style"
- "historical_campaign_ids": []
- "version": 1
- "updated_at": current UTC datetime in ISO format

Respond ONLY with a valid JSON object. No markdown fences. Be specific and evidence-based from the content provided.
