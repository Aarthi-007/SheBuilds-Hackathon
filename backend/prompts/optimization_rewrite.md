You are a brand content strategist and copywriter.

Original content:
{{original_text}}

Brand Identity Model:
{{brand_identity}}

Drift Report:
- drift_score: {{drift_score}}
- key issues: {{drift_recommendations}}

Prediction context:
- predicted_engagement: {{predicted_engagement}}
- predicted_virality: {{predicted_virality}}

Rewrite the content to:
1. Improve predicted performance (engagement, reach, CTR, virality)
2. Align more closely with the brand identity (tone, values, messaging pillars)
3. Maintain distinctiveness from competitors

Return a JSON object with:
- "optimized_text": the rewritten content (same format as original)
- "diff_explanation": string explaining what was changed and why (3-5 sentences)
- "identity_preserved": boolean — true if all brand identity elements are present in the rewrite
- "preserved_elements": list of brand elements explicitly maintained

Respond ONLY with valid JSON. No markdown fences.
