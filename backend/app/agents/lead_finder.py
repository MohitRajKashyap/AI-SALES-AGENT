import json
from typing import List
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.schemas import CompanyProfile, LeadCreate
from app.models.models import LeadStatus

logger = get_logger(__name__)

LEAD_FINDER_SYSTEM = """You are a B2B lead generation expert. Based on a company's profile, generate realistic potential customer leads.

Respond ONLY with a JSON array of lead objects:
[
  {
    "company_name": "string",
    "website": "https://example.com",
    "industry": "string",
    "email": "contact@example.com",
    "linkedin": "https://linkedin.com/company/example",
    "first_name": "string",
    "last_name": "string",
    "job_title": "string (decision maker role)",
    "lead_score": 0-100
  }
]

Generate realistic company names, actual decision-maker titles (CEO, CTO, VP Sales, etc.), and plausible contact info.
Lead score should reflect: industry fit (40%), company size fit (30%), engagement potential (30%)."""

LEAD_SCORER_SYSTEM = """You are a sales qualification expert. Score leads based on fit and potential.
Return JSON: {"score": 0-100, "status": "hot|warm|cold", "reasoning": "brief explanation"}
Hot: 70-100, Warm: 40-69, Cold: 0-39"""


class LeadFinderAgent:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def find_leads(self, company_profile: CompanyProfile, count: int = 10) -> List[dict]:
        logger.info(f"Finding {count} leads for {company_profile.company_name}")

        profile_summary = f"""
Company: {company_profile.company_name}
Industry: {company_profile.industry}
Services: {', '.join(company_profile.services[:5])}
Products: {', '.join(company_profile.products[:5])}
Target Customers: {', '.join(company_profile.target_customers[:5])}
Pain Points Solved: {', '.join(company_profile.pain_points[:5])}
"""
        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": LEAD_FINDER_SYSTEM},
                {"role": "user", "content": f"Generate {count} high-quality leads for this company:\n{profile_summary}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=3000,
        )

        raw = response.choices[0].message.content
        data = json.loads(raw)

        # Handle both array and object with array key
        if isinstance(data, list):
            leads = data
        else:
            leads = data.get("leads", list(data.values())[0] if data else [])

        return leads[:count]


class LeadScorerAgent:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def score_lead(self, lead: dict, company_profile: CompanyProfile) -> tuple[int, LeadStatus, str]:
        prompt = f"""
Company selling to: {company_profile.target_customers}
Lead: {json.dumps(lead)}
Score this lead's fit.
"""
        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": LEAD_SCORER_SYSTEM},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=200,
        )

        data = json.loads(response.choices[0].message.content)
        score = max(0, min(100, int(data.get("score", 50))))
        status_str = data.get("status", "cold")
        reasoning = data.get("reasoning", "")

        status_map = {"hot": LeadStatus.HOT, "warm": LeadStatus.WARM, "cold": LeadStatus.COLD}
        status = status_map.get(status_str, LeadStatus.COLD)

        return score, status, reasoning
