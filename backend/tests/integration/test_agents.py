import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.schemas.schemas import CompanyProfile
from app.models.models import LeadStatus


MOCK_PROFILE = CompanyProfile(
    company_name="TechCorp",
    industry="SaaS",
    services=["CRM", "Analytics"],
    products=["Dashboard Pro", "API Suite"],
    target_customers=["SMBs", "Enterprise"],
    pain_points=["Manual data entry", "Poor visibility"],
)

MOCK_LEADS = [
    {
        "company_name": "Acme Inc",
        "website": "https://acme.com",
        "industry": "FinTech",
        "email": "ceo@acme.com",
        "linkedin": "https://linkedin.com/company/acme",
        "first_name": "Jane",
        "last_name": "Smith",
        "job_title": "CEO",
        "lead_score": 82,
    },
    {
        "company_name": "Beta Corp",
        "website": "https://betacorp.io",
        "industry": "SaaS",
        "email": "founder@betacorp.io",
        "first_name": "Bob",
        "last_name": "Lee",
        "job_title": "Founder",
        "lead_score": 61,
    },
]

MOCK_EMAIL = {
    "subject": "Quick question about your data pipeline, Jane",
    "body": "Hi Jane,\n\nI noticed Acme has been scaling fast in FinTech...",
}


class TestWebsiteAnalyzerAgent:
    @pytest.mark.asyncio
    async def test_analyze_returns_profile(self):
        with patch("app.agents.website_analyzer.fetch_website_content", new=AsyncMock(return_value="Sample website content about SaaS company")) as _fetch, \
             patch("openai.AsyncOpenAI") as mock_openai:

            mock_response = MagicMock()
            mock_response.choices[0].message.content = '{"company_name":"TechCorp","industry":"SaaS","services":["CRM"],"products":["Dashboard"],"target_customers":["SMBs"],"pain_points":["Manual work"]}'
            mock_openai.return_value.chat.completions.create = AsyncMock(return_value=mock_response)

            from app.agents.website_analyzer import WebsiteAnalyzerAgent
            agent = WebsiteAnalyzerAgent()
            agent.client = mock_openai.return_value

            result = await agent.analyze("https://techcorp.com")
            assert result.company_name == "TechCorp"
            assert result.industry == "SaaS"
            assert isinstance(result.services, list)


class TestLeadFinderAgent:
    @pytest.mark.asyncio
    async def test_find_leads_returns_list(self):
        with patch("openai.AsyncOpenAI") as mock_openai:
            import json
            mock_response = MagicMock()
            mock_response.choices[0].message.content = json.dumps({"leads": MOCK_LEADS})
            mock_openai.return_value.chat.completions.create = AsyncMock(return_value=mock_response)

            from app.agents.lead_finder import LeadFinderAgent
            agent = LeadFinderAgent()
            agent.client = mock_openai.return_value

            leads = await agent.find_leads(MOCK_PROFILE, count=2)
            assert len(leads) <= 2
            assert all("company_name" in l for l in leads)

    @pytest.mark.asyncio
    async def test_lead_scorer_returns_tuple(self):
        with patch("openai.AsyncOpenAI") as mock_openai:
            import json
            mock_response = MagicMock()
            mock_response.choices[0].message.content = json.dumps({
                "score": 75,
                "status": "hot",
                "reasoning": "Strong industry fit"
            })
            mock_openai.return_value.chat.completions.create = AsyncMock(return_value=mock_response)

            from app.agents.lead_finder import LeadScorerAgent
            agent = LeadScorerAgent()
            agent.client = mock_openai.return_value

            score, status, reasoning = await agent.score_lead(MOCK_LEADS[0], MOCK_PROFILE)
            assert 0 <= score <= 100
            assert status in (LeadStatus.HOT, LeadStatus.WARM, LeadStatus.COLD)
            assert isinstance(reasoning, str)


class TestEmailGeneratorAgent:
    @pytest.mark.asyncio
    async def test_generate_email_returns_subject_and_body(self):
        with patch("openai.AsyncOpenAI") as mock_openai:
            import json
            mock_response = MagicMock()
            mock_response.choices[0].message.content = json.dumps(MOCK_EMAIL)
            mock_openai.return_value.chat.completions.create = AsyncMock(return_value=mock_response)

            from app.agents.email_generator import EmailGeneratorAgent
            from app.models.models import EmailType, EmailStyle
            agent = EmailGeneratorAgent()
            agent.client = mock_openai.return_value

            result = await agent.generate_email(
                sender_company=MOCK_PROFILE.model_dump(),
                lead=MOCK_LEADS[0],
                email_type=EmailType.COLD,
                email_style=EmailStyle.PROFESSIONAL,
            )
            assert "subject" in result
            assert "body" in result
            assert len(result["subject"]) > 0
            assert len(result["body"]) > 0


class TestEmailTracking:
    def test_tracking_pixel_constant(self):
        from app.api.v1.endpoints.tracking import TRACKING_PIXEL
        assert isinstance(TRACKING_PIXEL, bytes)
        assert len(TRACKING_PIXEL) > 0
        # GIF magic bytes
        assert TRACKING_PIXEL[:3] == b"GIF"

    def test_build_tracking_pixel_html(self):
        from app.utils.email_utils import build_tracking_pixel_html
        html = build_tracking_pixel_html("test-uuid-123", "https://app.example.com")
        assert "test-uuid-123" in html
        assert "<img" in html

    def test_plain_to_html_includes_pixel(self):
        from app.utils.email_utils import plain_to_html
        html = plain_to_html("Hello world\nSecond line", "tid-456", "https://app.example.com")
        assert "tid-456" in html
        assert "<br>" in html
        assert "<!DOCTYPE html>" in html
