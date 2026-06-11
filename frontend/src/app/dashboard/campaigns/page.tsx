'use client'
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { campaignApi } from '@/lib/api'
import { useAuthStore } from '@/store/auth'
import { Megaphone, Plus, Play, Pause, Trash2, Loader2 } from 'lucide-react'
import type { Campaign, CampaignStatus, EmailStyle } from '@/types'

const statusColors: Record<CampaignStatus, string> = {
  draft: 'text-slate-400 bg-slate-500/10 border-slate-500/20',
  active: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  paused: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
  completed: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
  deleted: 'text-red-400 bg-red-500/10 border-red-500/20',
}

function CreateCampaignModal({ onClose }: { onClose: () => void }) {
  const { workspace } = useAuthStore()
  const qc = useQueryClient()
  const [form, setForm] = useState({
    name: '', description: '', goal: '', daily_limit: 50,
    email_style: 'professional' as EmailStyle, target_industry: '',
    followup_days: [3, 7, 14],
  })

  const create = useMutation({
    mutationFn: () => campaignApi.create(workspace!.id, form),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['campaigns'] }); onClose() },
  })

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-lg p-6">
        <h2 className="text-white font-semibold text-lg mb-5">New Campaign</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-slate-300 mb-1.5">Campaign Name *</label>
            <input value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
              placeholder="Q4 Enterprise Outreach"
              className="w-full px-4 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 text-sm" />
          </div>
          <div>
            <label className="block text-sm text-slate-300 mb-1.5">Goal</label>
            <input value={form.goal} onChange={e => setForm(f => ({ ...f, goal: e.target.value }))}
              placeholder="Book 10 discovery calls with SaaS companies"
              className="w-full px-4 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 text-sm" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-slate-300 mb-1.5">Email Style</label>
              <select value={form.email_style} onChange={e => setForm(f => ({ ...f, email_style: e.target.value as EmailStyle }))}
                className="w-full px-4 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-blue-500 text-sm">
                <option value="professional">Professional</option>
                <option value="friendly">Friendly</option>
                <option value="startup">Startup</option>
                <option value="enterprise">Enterprise</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-slate-300 mb-1.5">Daily Limit</label>
              <input type="number" value={form.daily_limit} onChange={e => setForm(f => ({ ...f, daily_limit: Number(e.target.value) }))}
                min={1} max={500}
                className="w-full px-4 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-blue-500 text-sm" />
            </div>
          </div>
          <div>
            <label className="block text-sm text-slate-300 mb-1.5">Target Industry</label>
            <input value={form.target_industry} onChange={e => setForm(f => ({ ...f, target_industry: e.target.value }))}
              placeholder="SaaS, FinTech, Healthcare..."
              className="w-full px-4 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 text-sm" />
          </div>
          <div className="flex gap-3 pt-2">
            <button onClick={onClose} className="flex-1 py-2.5 rounded-xl border border-slate-700 text-slate-400 hover:text-white text-sm transition">Cancel</button>
            <button onClick={() => create.mutate()} disabled={!form.name || create.isPending}
              className="flex-1 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium transition disabled:opacity-50">
              {create.isPending ? 'Creating...' : 'Create Campaign'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function CampaignsPage() {
  const { workspace } = useAuthStore()
  const qc = useQueryClient()
  const [showModal, setShowModal] = useState(false)

  const { data: campaigns = [], isLoading } = useQuery<Campaign[]>({
    queryKey: ['campaigns', workspace?.id],
    queryFn: () => campaignApi.list(workspace!.id).then(r => r.data),
    enabled: !!workspace,
  })

  const pauseMutation = useMutation({
    mutationFn: (id: string) => campaignApi.pause(workspace!.id, id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['campaigns'] }),
  })
  const resumeMutation = useMutation({
    mutationFn: (id: string) => campaignApi.resume(workspace!.id, id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['campaigns'] }),
  })
  const deleteMutation = useMutation({
    mutationFn: (id: string) => campaignApi.delete(workspace!.id, id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['campaigns'] }),
  })

  const active = campaigns.filter(c => c.status !== 'deleted')

  return (
    <div className="p-6 space-y-6">
      {showModal && <CreateCampaignModal onClose={() => setShowModal(false)} />}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Campaigns</h1>
          <p className="text-slate-400 text-sm mt-1">{active.length} campaigns</p>
        </div>
        <button onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-sm font-medium transition">
          <Plus size={16} /> New Campaign
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-16"><Loader2 className="animate-spin text-blue-500" size={24} /></div>
      ) : active.length === 0 ? (
        <div className="text-center py-16 bg-slate-900 border border-slate-800 rounded-xl">
          <Megaphone size={32} className="mx-auto text-slate-600 mb-3" />
          <p className="text-slate-400 font-medium">No campaigns yet</p>
          <p className="text-slate-500 text-sm mt-1">Create a campaign to start reaching out to leads</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {active.map(campaign => (
            <div key={campaign.id} className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-1">
                    <h3 className="text-white font-semibold">{campaign.name}</h3>
                    <span className={`px-2 py-0.5 rounded-full text-xs border font-medium ${statusColors[campaign.status]}`}>
                      {campaign.status}
                    </span>
                  </div>
                  {campaign.goal && <p className="text-slate-400 text-sm">{campaign.goal}</p>}
                  <div className="flex items-center gap-4 mt-3 text-xs text-slate-500">
                    <span>Style: <span className="text-slate-300">{campaign.email_style}</span></span>
                    <span>Daily limit: <span className="text-slate-300">{campaign.daily_limit}</span></span>
                    <span>Follow-ups: <span className="text-slate-300">Day {campaign.followup_days.join(', ')}</span></span>
                    {campaign.target_industry && <span>Industry: <span className="text-slate-300">{campaign.target_industry}</span></span>}
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  {campaign.status === 'active' ? (
                    <button onClick={() => pauseMutation.mutate(campaign.id)}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-amber-500/30 text-amber-400 hover:bg-amber-500/10 text-xs transition">
                      <Pause size={12} /> Pause
                    </button>
                  ) : campaign.status === 'paused' ? (
                    <button onClick={() => resumeMutation.mutate(campaign.id)}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10 text-xs transition">
                      <Play size={12} /> Resume
                    </button>
                  ) : null}
                  <button onClick={() => deleteMutation.mutate(campaign.id)}
                    className="p-1.5 rounded-lg text-slate-600 hover:text-red-400 hover:bg-red-500/10 transition">
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
