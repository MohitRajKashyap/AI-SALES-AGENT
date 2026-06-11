'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { workspaceApi } from '@/lib/api'
import { useAuthStore } from '@/store/auth'
import { Building2, ArrowRight, Loader2 } from 'lucide-react'

export default function OnboardingPage() {
  const router = useRouter()
  const { setWorkspace, setWorkspaces } = useAuthStore()
  const [form, setForm] = useState({ name: '', website: '', industry: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const { data: workspace } = await workspaceApi.create(form)
      setWorkspace(workspace)
      setWorkspaces([workspace])
      router.push('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create workspace')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 p-4">
      <div className="w-full max-w-lg">
        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center mx-auto mb-4">
            <Building2 size={24} className="text-blue-400" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Create your workspace</h1>
          <p className="text-slate-400">Set up your company workspace to get started with AI-powered sales</p>
        </div>
        <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-8">
          {error && <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">Company / Workspace Name *</label>
              <input value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                placeholder="Acme Corp" required
                className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">Website (optional)</label>
              <input value={form.website} onChange={e => setForm(f => ({ ...f, website: e.target.value }))}
                placeholder="https://acme.com" type="url"
                className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">Industry (optional)</label>
              <input value={form.industry} onChange={e => setForm(f => ({ ...f, industry: e.target.value }))}
                placeholder="SaaS, E-commerce, Consulting..."
                className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition text-sm" />
            </div>
            <button type="submit" disabled={loading || !form.name}
              className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold transition disabled:opacity-50 mt-2">
              {loading ? <Loader2 size={18} className="animate-spin" /> : <ArrowRight size={18} />}
              {loading ? 'Creating workspace...' : 'Create & Continue'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
