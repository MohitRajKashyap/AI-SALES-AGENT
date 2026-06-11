import json
from typing import TypedDict, Annotated, Optional, List
from datetime import datetime, timezone

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.core.logging import get_logger
from app.agents.website_analyzer import WebsiteAnalyzerAgent
from app.agents.lead_finder import LeadFinderAgent, LeadScorerAgent
from app.agents.email_generator import EmailGeneratorAgent, FollowUpPlannerAgent

logger = get_logger(__name__)


class AgentState(TypedDict):
    url: str
    workspace_id: str
    company_profile: Optional[dict]
    raw_leads: Optional[List[dict]]
    scored_leads: Optional[List[dict]]
    emails: Optional[List[dict]]
    followup_plans: Optional[List[dict]]
    errors: List[str]
    current_step: str
    tokens_used: int


async def website_analyzer_node(state: AgentState) -> AgentState:
    logger.info(f"[Graph] Website Analyzer running for {state['url']}")
    agent = WebsiteAnalyzerAgent()
    try:
        profile = await agent.analyze(state["url"])
        return {**state, "company_profile": profile.model_dump(), "current_step": "website_analyzed"}
    except Exception as e:
        logger.error(f"Website analyzer failed: {e}")
        return {**state, "errors": [*state["errors"], str(e)], "current_step": "failed"}


async def lead_finder_node(state: AgentState) -> AgentState:
    logger.info("[Graph] Lead Finder running")
    agent = LeadFinderAgent()
    from app.schemas.schemas import CompanyProfile
    try:
        profile = CompanyProfile(**state["company_profile"])
        leads = await agent.find_leads(profile, count=10)
        return {**state, "raw_leads": leads, "current_step": "leads_found"}
    except Exception as e:
        logger.error(f"Lead finder failed: {e}")
        return {**state, "errors": [*state["errors"], str(e)], "current_step": "failed"}


async def lead_scorer_node(state: AgentState) -> AgentState:
    logger.info("[Graph] Lead Scorer running")
    agent = LeadScorerAgent()
    from app.schemas.schemas import CompanyProfile
    profile = CompanyProfile(**state["company_profile"])
    scored = []

    for lead in state.get("raw_leads", []):
        try:
            score, status, reasoning = await agent.score_lead(lead, profile)
            scored.append({**lead, "lead_score": score, "status": status.value, "reasoning": reasoning})
        except Exception as e:
            scored.append({**lead, "lead_score": 30, "status": "cold"})

    scored.sort(key=lambda x: x["lead_score"], reverse=True)
    return {**state, "scored_leads": scored, "current_step": "leads_scored"}


async def email_generator_node(state: AgentState) -> AgentState:
    logger.info("[Graph] Email Generator running for top leads")
    agent = EmailGeneratorAgent()
    emails = []
    top_leads = state.get("scored_leads", [])[:5]

    for lead in top_leads:
        try:
            email = await agent.generate_email(
                sender_company=state["company_profile"],
                lead=lead,
                email_type="cold",
            )
            emails.append({"lead_id": lead.get("company_name"), "email": email})
        except Exception as e:
            logger.warning(f"Email gen failed for {lead.get('company_name')}: {e}")

    return {**state, "emails": emails, "current_step": "emails_generated"}


async def followup_planner_node(state: AgentState) -> AgentState:
    logger.info("[Graph] Follow-Up Planner running")
    agent = FollowUpPlannerAgent()
    plans = []

    for email_data in (state.get("emails") or [])[:3]:
        try:
            plan = await agent.plan_followups(
                lead={},
                initial_email=email_data["email"],
                followup_days=[3, 7, 14]
            )
            plans.append({"lead": email_data["lead_id"], "plan": plan})
        except Exception as e:
            logger.warning(f"Followup planner failed: {e}")

    return {**state, "followup_plans": plans, "current_step": "completed"}


def should_continue(state: AgentState) -> str:
    if state["current_step"] == "failed":
        return END
    return "continue"


def build_sales_workflow() -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("website_analyzer", website_analyzer_node)
    workflow.add_node("lead_finder", lead_finder_node)
    workflow.add_node("lead_scorer", lead_scorer_node)
    workflow.add_node("email_generator", email_generator_node)
    workflow.add_node("followup_planner", followup_planner_node)

    workflow.set_entry_point("website_analyzer")
    workflow.add_edge("website_analyzer", "lead_finder")
    workflow.add_edge("lead_finder", "lead_scorer")
    workflow.add_edge("lead_scorer", "email_generator")
    workflow.add_edge("email_generator", "followup_planner")
    workflow.add_edge("followup_planner", END)

    return workflow.compile()


async def run_full_pipeline(url: str, workspace_id: str) -> AgentState:
    graph = build_sales_workflow()
    initial_state: AgentState = {
        "url": url,
        "workspace_id": workspace_id,
        "company_profile": None,
        "raw_leads": None,
        "scored_leads": None,
        "emails": None,
        "followup_plans": None,
        "errors": [],
        "current_step": "starting",
        "tokens_used": 0,
    }

    result = await graph.ainvoke(initial_state)
    return result
