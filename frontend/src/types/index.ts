export interface User {
  id: string
  email: string
  full_name: string
  avatar_url?: string
  is_active: boolean
  is_superuser: boolean
  role: 'admin' | 'owner' | 'member'
  created_at: string
}

export interface Workspace {
  id: string
  name: string
  slug: string
  logo_url?: string
  website?: string
  industry?: string
  owner_id: string
  created_at: string
}

export interface CompanyProfile {
  id: string
  workspace_id: string
  website_url: string
  company_name?: string
  industry?: string
  services?: string[]
  products?: string[]
  target_customers?: string[]
  pain_points?: string[]
  created_at: string
}

export type LeadStatus = 'hot' | 'warm' | 'cold' | 'converted' | 'disqualified'

export interface Lead {
  id: string
  workspace_id: string
  company_id?: string
  company_name: string
  website?: string
  industry?: string
  email?: string
  linkedin?: string
  first_name?: string
  last_name?: string
  job_title?: string
  phone?: string
  lead_score: number
  status: LeadStatus
  tags?: string[]
  notes?: string
  created_at: string
}

export type CampaignStatus = 'draft' | 'active' | 'paused' | 'completed' | 'deleted'
export type EmailStyle = 'professional' | 'friendly' | 'startup' | 'enterprise'

export interface Campaign {
  id: string
  workspace_id: string
  name: string
  description?: string
  status: CampaignStatus
  goal?: string
  daily_limit: number
  email_style: EmailStyle
  followup_days: number[]
  target_industry?: string
  created_at: string
}

export type EmailType = 'cold' | 'followup' | 'meeting_request' | 'product_intro'
export type EmailStatus = 'draft' | 'queued' | 'sent' | 'opened' | 'replied' | 'bounced' | 'failed'

export interface Email {
  id: string
  campaign_id?: string
  lead_id: string
  subject: string
  body: string
  email_type: EmailType
  email_style: EmailStyle
  status: EmailStatus
  sent_at?: string
  opened_at?: string
  replied_at?: string
  followup_day?: number
  created_at: string
}

export interface DashboardMetrics {
  total_leads: number
  emails_sent: number
  replies: number
  meetings_booked: number
  conversion_rate: number
  hot_leads: number
  warm_leads: number
  active_campaigns: number
}

export interface DailyAnalytics {
  date: string
  emails_sent: number
  emails_opened: number
  replies: number
  new_leads: number
  meetings_booked: number
}

export interface CampaignPerformance {
  campaign_id: string
  campaign_name: string
  emails_sent: number
  open_rate: number
  reply_rate: number
}

export interface AgentLog {
  id: string
  workspace_id: string
  agent_type: string
  status: 'running' | 'completed' | 'failed'
  input_data?: Record<string, unknown>
  output_data?: Record<string, unknown>
  error_message?: string
  tokens_used: number
  duration_seconds?: number
  created_at: string
  completed_at?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}
