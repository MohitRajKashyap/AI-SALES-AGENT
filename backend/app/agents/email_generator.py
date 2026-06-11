import json
from typing import Optional
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logging import get_logger
from app.models.models import EmailType, EmailStyle

logger = get_logger(__name__)


EMAIL_STYLES = {
    EmailStyle.PROFESSIONAL: "formal, data-driven, ROI-focused",
    EmailStyle.FRIENDLY: "conversational, warm, relationship-first",
    EmailStyle.STARTUP: "bold, direct, growth-focused, casual",
    EmailStyle.ENTERPRISE: "executive-level, strategic, compliance-aware",
}

EMAIL_TYPE_INSTRUCTIONS = {
    EmailType.COLD: "This is a first-touch cold outreach. Be brief, value-first. Max 150 words body.",
    EmailType.FOLLOWUP: "Reference the previous unreplied email. Add a new angle. Max 100 words.",
    EmailType.MEETING_REQUEST: "Request a specific 15-minute meeting. Offer calendar link. Max 120 words.",
    EmailType.PRODUCT_INTRO: "Introduce a specific product/service. Focus on one key benefit. Max 160 words.",
}

EMAIL_GENERATOR_SYSTEM = """You are an expert B2B sales copywriter. Generate highly personalized, conversion-optimized sales emails.

Respond ONLY with JSON:
{
  "subject": "compelling subject line under 60 chars",
  "body": "email body text with proper line breaks"
}

Rules:
- Use the prospect's name and company
- Reference specific pain points relevant to their industry
- Clear, single CTA
- No generic phrases like "I hope this finds you well"
- Personalized first line referencing their specific situation"""


class EmailGeneratorAgent:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_email(
        self,
        sender_company: dict,
        lead: dict,
        email_type: EmailType = EmailType.COLD,
        email_style: EmailStyle = EmailStyle.PROFESSIONAL,
        campaign_goal: Optional[str] = None,
        followup_day: Optional[int] = None,
    ) -> dict:
        style_desc = EMAIL_STYLES.get(email_style, "professional")
        type_instruction = EMAIL_TYPE_INSTRUCTIONS.get(email_type, "")

        followup_context = ""
        if followup_day:
            followup_context = f"\nThis is Day {followup_day} follow-up after no reply to initial email."

        prompt = f"""
Sender Company:
- Name: {sender_company.get('company_name', 'Our Company')}
- Industry: {sender_company.get('industry', '')}
- Services: {', '.join(sender_company.get('services', [])[:3])}
- Value Proposition: {', '.join(sender_company.get('pain_points', [])[:2])}

Prospect:
- Name: {lead.get('first_name', '')} {lead.get('last_name', '')}
- Title: {lead.get('job_title', 'Decision Maker')}
- Company: {lead.get('company_name', '')}
- Industry: {lead.get('industry', '')}

Email Style: {style_desc}
Type: {type_instruction}{followup_context}
{f'Campaign Goal: {campaign_goal}' if campaign_goal else ''}

Generate the email now.
"""

        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": EMAIL_GENERATOR_SYSTEM},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.8,
            max_tokens=800,
        )

        return json.loads(response.choices[0].message.content)


class FollowUpPlannerAgent:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def plan_followups(self, lead: dict, initial_email: dict, followup_days: list[int]) -> list[dict]:
        prompt = f"""
Lead: {json.dumps(lead)}
Initial Email Subject: {initial_email.get('subject')}
Plan follow-ups for days: {followup_days}

Return JSON array with one object per follow-up day:
[{{"day": 3, "angle": "new value angle", "suggested_subject": "...", "suggested_cta": "..."}}]"""

        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a B2B sales follow-up strategist. Plan varied, non-repetitive follow-up angles."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=600,
        )

        data = json.loads(response.choices[0].message.content)
        if isinstance(data, list):
            return data
        return data.get("followups", list(data.values())[0] if data else [])
