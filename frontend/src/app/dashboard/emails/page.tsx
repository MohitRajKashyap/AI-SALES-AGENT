'use client'
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { emailApi, leadApi } from '@/lib/api'
import { useAuthStore } from '@/store/auth'
import { Mail, Wand2, Loader2, ChevronDown, ChevronRight, Copy, Check } from 'lucide-react'
import type { Email, PaginatedResponse } from '@/types'

const statusColors: Record<string, string> = {
  draft: 'text-slate-400 bg-slate-500/10',
  queued: 'text-amber-400 bg-amber-500/10',
  sent: 'text-blue-400 bg-blue-500/10',
  opened: 'text-purple-400 bg-purple-500/10',
  replied: 'text-emerald-400 bg-emerald-500/10',
  bounced: 'text-red-400 bg-red-500/10',
  failed: 'text-red-400 bg-red-500/10',
}

function EmailCard({ email }: { email: Email }) {
  const [expanded, setExpanded] = useState(false)
  const [copied, setCopied] = useState(false)

  const copy = () => {
    navigator.clipboard.writeText(`Subject: ${email.subject}\n\n${email.body}`)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl hover:border-slate-700 transition">
      <div className="flex items-start gap-4 p-5 cursor-pointer" onClick={() => setExpanded(!expanded)}>
        <div className="w-8 h-8 rounded-lg bg-blue-600/20 flex items-center justify-center flex-shrink-0">
          <Mail size={14} className="text-blue-400" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-1">
            <p className="text-white font-medium text-sm truncate">{email.subject}</p>
            <span className={`px-2 py-0.5 rounded-full text-xs font-medium flex-shrink-0 ${statusColors[email.status]}`}>
              {email.status}
            </span>
          </div>
          <p className="text-slate-500 text-xs">
            {email.email_type} · {email.email_style} · {new Date(email.created_at).toLocaleDateString()}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={e => { e.stopPropagation(); copy() }} className="p-1.5 text-slate-500 hover:text-white transition">
            {copied ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
          </button>
          {expanded ? <ChevronDown size={16} className="text-slate-400" /> : <ChevronRight size={16} className="text-slate-400" />}
        </div>
      </div>
      {expanded && (
        <div className="px-5 pb-5 border-t border-slate-800/50 pt-4">
          <pre className="text-slate-300 text-sm whitespace-pre-wrap leading-relaxed font-sans">{email.body}</pre>
        </div>
      )}
    </div>
  )
}

function GenerateEmailModal({ onClose }: { onClose: () => void }) {
  const { workspace } = useAuthStore()
  const qc = useQueryClient()
  const [form, setForm] = useState({
    lead_id: '', email_type: 'cold', email_style: 'professional', custom_goal: '',
  })

  const { data: leadsData } = useQuery({
    queryKey: ['leads-simple', workspace?.id],
    queryFn: () => leadApi.list(workspace!.id, { page_size: 100 }).then(r => r.data),
    enabled: !!workspace,
  })

  const generate = useMutation({
    mutationFn: () => emailApi.generate(workspace!.id, form),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['emails'] }); onClose() },
  })

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-lg p-6">
        <div className="flex items-center gap-2 mb-5">
          <Wand2 size={18} className="text-blue-400" />
          <h2 className="text-white font-semibold text-lg">Generate AI Email</h2>
        </div>
        {generate.isPending ? (
          <div className="text-center py-8">
            <Loader2 className="animate-spin mx-auto mb-3 text-blue-500" size={28} />
            <p className="text-white font-medium">Crafting personalized email…</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-slate-300 mb-1.5">Select Lead *</label>
              <select value={form.lead_id} onChange={e => setForm(f => ({ ...f, lead_id: e.target.value }))}
                className="w-full px-4 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-blue-500 text-sm">
                <option value="">Choose a lead...</option>
                {leadsData?.items?.map((l: any) => (
                  <option key={l.id} value={l.id}>{l.company_name} — {l.first_name} {l.last_name}</option>
                ))}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-slate-300 mb-1.5">Email Type</label>
                <select value={form.email_type} onChange={e => setForm(f => ({ ...f, email_type: e.target.value }))}
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-blue-500 text-sm">
                  <option value="cold">Cold Outreach</option>
                  <option value="followup">Follow-up</option>
                  <option value="meeting_request">Meeting Request</option>
                  <option value="product_intro">Product Intro</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-slate-300 mb-1.5">Writing Style</label>
                <select value={form.email_style} onChange={e => setForm(f => ({ ...f, email_style: e.target.value }))}
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-blue-500 text-sm">
                  <option value="professional">Professional</option>
                  <option value="friendly">Friendly</option>
                  <option value="startup">Startup</option>
                  <option value="enterprise">Enterprise</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm text-slate-300 mb-1.5">Custom Goal (optional)</label>
              <input value={form.custom_goal} onChange={e => setForm(f => ({ ...f, custom_goal: e.target.value }))}
                placeholder="Book a 15-minute intro call"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 text-sm" />
            </div>
            {generate.isError && <p className="text-red-400 text-sm">{(generate.error as any)?.response?.data?.detail || 'Failed to generate email'}</p>}
            <div className="flex gap-3 pt-2">
              <button onClick={onClose} className="flex-1 py-2.5 rounded-xl border border-slate-700 text-slate-400 hover:text-white text-sm transition">Cancel</button>
              <button onClick={() => generate.mutate()} disabled={!form.lead_id || generate.isPending}
                className="flex-1 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium transition disabled:opacity-50">
                Generate Email
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default function EmailsPage() {
  const { workspace } = useAuthStore()
  const [page, setPage] = useState(1)
  const [showModal, setShowModal] = useState(false)

  const { data, isLoading } = useQuery<PaginatedResponse<Email>>({
    queryKey: ['emails', workspace?.id, page],
    queryFn: () => emailApi.list(workspace!.id, { page, page_size: 20 }).then(r => r.data),
    enabled: !!workspace,
  })

  return (
    <div className="p-6 space-y-6">
      {showModal && <GenerateEmailModal onClose={() => setShowModal(false)} />}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Emails</h1>
          <p className="text-slate-400 text-sm mt-1">{data?.total ?? 0} total emails</p>
        </div>
        <button onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-sm font-medium transition">
          <Wand2 size={16} /> Generate Email
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-16"><Loader2 className="animate-spin text-blue-500" size={24} /></div>
      ) : data?.items.length === 0 ? (
        <div className="text-center py-16 bg-slate-900 border border-slate-800 rounded-xl">
          <Mail size={32} className="mx-auto text-slate-600 mb-3" />
          <p className="text-slate-400 font-medium">No emails yet</p>
          <p className="text-slate-500 text-sm mt-1">Generate your first AI-personalized email</p>
        </div>
      ) : (
        <div className="space-y-3">
          {data?.items.map(email => <EmailCard key={email.id} email={email} />)}
        </div>
      )}

      {data && data.pages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-slate-400 text-sm">Page {page} of {data.pages}</p>
          <div className="flex gap-2">
            <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}
              className="px-3 py-1.5 rounded-lg border border-slate-700 text-slate-400 text-sm disabled:opacity-40 hover:border-slate-600">Previous</button>
            <button onClick={() => setPage(p => Math.min(data.pages, p + 1))} disabled={page === data.pages}
              className="px-3 py-1.5 rounded-lg border border-slate-700 text-slate-400 text-sm disabled:opacity-40 hover:border-slate-600">Next</button>
          </div>
        </div>
      )}
    </div>
  )
}
