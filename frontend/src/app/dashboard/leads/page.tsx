'use client'
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { leadApi, companyApi } from '@/lib/api'
import { useAuthStore } from '@/store/auth'
import { Users, Plus, Search, Flame, Zap, Snowflake, Globe, Loader2, Trash2, ExternalLink } from 'lucide-react'
import type { Lead, LeadStatus, PaginatedResponse } from '@/types'

const statusConfig: Record<LeadStatus, { label: string; color: string; icon: any }> = {
  hot: { label: 'Hot', color: 'text-red-400 bg-red-500/10 border-red-500/20', icon: Flame },
  warm: { label: 'Warm', color: 'text-amber-400 bg-amber-500/10 border-amber-500/20', icon: Zap },
  cold: { label: 'Cold', color: 'text-blue-400 bg-blue-500/10 border-blue-500/20', icon: Snowflake },
  converted: { label: 'Converted', color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20', icon: Users },
  disqualified: { label: 'DQ', color: 'text-slate-400 bg-slate-500/10 border-slate-500/20', icon: Users },
}

function LeadScoreBadge({ score }: { score: number }) {
  const color = score >= 70 ? 'text-red-400' : score >= 40 ? 'text-amber-400' : 'text-blue-400'
  return <span className={`font-bold text-sm ${color}`}>{score}</span>
}

function GenerateLeadsModal({ onClose }: { onClose: () => void }) {
  const { workspace } = useAuthStore()
  const qc = useQueryClient()
  const [url, setUrl] = useState('')
  const [count, setCount] = useState(10)
  const [step, setStep] = useState<'url' | 'generating'>('url')

  const generate = useMutation({
    mutationFn: async () => {
      const { data: company } = await companyApi.analyze(workspace!.id, url)
      return leadApi.generate(workspace!.id, { company_id: company.id, count })
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['leads'] })
      onClose()
    },
  })

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-md p-6">
        <h2 className="text-white font-semibold text-lg mb-1">Generate Leads with AI</h2>
        <p className="text-slate-400 text-sm mb-5">Enter your company website — our AI will analyze it and find matching prospects.</p>

        {generate.isPending ? (
          <div className="text-center py-8">
            <Loader2 className="animate-spin mx-auto mb-3 text-blue-500" size={32} />
            <p className="text-white font-medium">AI is working…</p>
            <p className="text-slate-400 text-sm mt-1">Analyzing website → Finding leads → Scoring prospects</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-slate-300 mb-1.5">Your Company Website</label>
              <input
                type="url"
                value={url}
                onChange={e => setUrl(e.target.value)}
                placeholder="https://yourcompany.com"
                className="w-full px-4 py-3 rounded-xl bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm text-slate-300 mb-1.5">Number of leads: <span className="text-blue-400 font-medium">{count}</span></label>
              <input type="range" min={5} max={50} step={5} value={count} onChange={e => setCount(Number(e.target.value))} className="w-full accent-blue-500" />
            </div>
            {generate.isError && (
              <p className="text-red-400 text-sm">{(generate.error as any)?.response?.data?.detail || 'Failed to generate leads'}</p>
            )}
            <div className="flex gap-3 pt-2">
              <button onClick={onClose} className="flex-1 py-2.5 rounded-xl border border-slate-700 text-slate-400 hover:text-white hover:border-slate-600 text-sm transition">Cancel</button>
              <button
                onClick={() => generate.mutate()}
                disabled={!url}
                className="flex-1 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm transition disabled:opacity-50"
              >
                Generate {count} Leads
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default function LeadsPage() {
  const { workspace } = useAuthStore()
  const qc = useQueryClient()
  const [page, setPage] = useState(1)
  const [filterStatus, setFilterStatus] = useState<LeadStatus | ''>('')
  const [search, setSearch] = useState('')
  const [showModal, setShowModal] = useState(false)

  const { data, isLoading } = useQuery<PaginatedResponse<Lead>>({
    queryKey: ['leads', workspace?.id, page, filterStatus],
    queryFn: () => leadApi.list(workspace!.id, { page, page_size: 20, status: filterStatus || undefined }).then(r => r.data),
    enabled: !!workspace,
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => leadApi.delete(workspace!.id, id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['leads'] }),
  })

  const leads = data?.items ?? []
  const filtered = search ? leads.filter(l =>
    l.company_name.toLowerCase().includes(search.toLowerCase()) ||
    l.email?.toLowerCase().includes(search.toLowerCase()) ||
    l.industry?.toLowerCase().includes(search.toLowerCase())
  ) : leads

  return (
    <div className="p-6 space-y-6">
      {showModal && <GenerateLeadsModal onClose={() => setShowModal(false)} />}

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Leads</h1>
          <p className="text-slate-400 text-sm mt-1">{data?.total ?? 0} total prospects</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-sm font-medium transition"
        >
          <Plus size={16} /> Generate with AI
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-3 flex-wrap">
        <div className="relative flex-1 min-w-48">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search leads..."
            className="w-full pl-9 pr-4 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>
        <div className="flex gap-2">
          {(['', 'hot', 'warm', 'cold'] as const).map(s => (
            <button
              key={s}
              onClick={() => setFilterStatus(s)}
              className={`px-3 py-2 rounded-xl text-xs font-medium border transition ${filterStatus === s ? 'bg-blue-600 border-blue-600 text-white' : 'border-slate-700 text-slate-400 hover:border-slate-600'}`}
            >
              {s === '' ? 'All' : s.charAt(0).toUpperCase() + s.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="animate-spin text-blue-500" size={24} />
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16">
            <Users size={32} className="mx-auto text-slate-600 mb-3" />
            <p className="text-slate-400 font-medium">No leads yet</p>
            <p className="text-slate-500 text-sm mt-1">Click "Generate with AI" to find your first prospects</p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead className="border-b border-slate-800">
              <tr className="text-slate-400">
                <th className="text-left px-5 py-3 font-medium">Company</th>
                <th className="text-left px-5 py-3 font-medium">Contact</th>
                <th className="text-left px-5 py-3 font-medium">Industry</th>
                <th className="text-center px-5 py-3 font-medium">Score</th>
                <th className="text-left px-5 py-3 font-medium">Status</th>
                <th className="px-5 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {filtered.map(lead => {
                const cfg = statusConfig[lead.status]
                const Icon = cfg.icon
                return (
                  <tr key={lead.id} className="hover:bg-slate-800/30 transition group">
                    <td className="px-5 py-4">
                      <div className="font-medium text-white">{lead.company_name}</div>
                      {lead.website && (
                        <a href={lead.website} target="_blank" rel="noopener noreferrer" className="text-slate-500 text-xs flex items-center gap-1 hover:text-slate-300 mt-0.5">
                          <Globe size={10} /> {lead.website.replace(/https?:\/\//, '')}
                        </a>
                      )}
                    </td>
                    <td className="px-5 py-4">
                      <div className="text-slate-300">{lead.first_name} {lead.last_name}</div>
                      <div className="text-slate-500 text-xs">{lead.job_title}</div>
                      {lead.email && <div className="text-slate-500 text-xs">{lead.email}</div>}
                    </td>
                    <td className="px-5 py-4 text-slate-400">{lead.industry || '—'}</td>
                    <td className="px-5 py-4 text-center"><LeadScoreBadge score={lead.lead_score} /></td>
                    <td className="px-5 py-4">
                      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full border text-xs font-medium ${cfg.color}`}>
                        <Icon size={10} /> {cfg.label}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition">
                        {lead.linkedin && (
                          <a href={lead.linkedin} target="_blank" rel="noopener noreferrer" className="text-slate-400 hover:text-white">
                            <ExternalLink size={14} />
                          </a>
                        )}
                        <button onClick={() => deleteMutation.mutate(lead.id)} className="text-slate-600 hover:text-red-400 transition">
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      {data && data.pages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-slate-400 text-sm">Page {page} of {data.pages}</p>
          <div className="flex gap-2">
            <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="px-3 py-1.5 rounded-lg border border-slate-700 text-slate-400 text-sm disabled:opacity-40 hover:border-slate-600">Previous</button>
            <button onClick={() => setPage(p => Math.min(data.pages, p + 1))} disabled={page === data.pages} className="px-3 py-1.5 rounded-lg border border-slate-700 text-slate-400 text-sm disabled:opacity-40 hover:border-slate-600">Next</button>
          </div>
        </div>
      )}
    </div>
  )
}
