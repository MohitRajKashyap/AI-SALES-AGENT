'use client'
import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { authApi, workspaceApi } from '@/lib/api'
import { useAuthStore } from '@/store/auth'
import { Settings, User, Building2, Bell, Shield, Check } from 'lucide-react'

function Section({ title, icon: Icon, children }: { title: string; icon: any; children: React.ReactNode }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-5">
        <Icon size={18} className="text-slate-400" />
        <h2 className="text-white font-semibold">{title}</h2>
      </div>
      {children}
    </div>
  )
}

export default function SettingsPage() {
  const { user, workspace, setUser, setWorkspace } = useAuthStore()
  const qc = useQueryClient()
  const [saved, setSaved] = useState<string | null>(null)

  const [profileForm, setProfileForm] = useState({ full_name: user?.full_name || '' })
  const [wsForm, setWsForm] = useState({ name: workspace?.name || '', website: workspace?.website || '', industry: workspace?.industry || '' })

  const saveProfile = useMutation({
    mutationFn: () => authApi.updateMe(profileForm),
    onSuccess: ({ data }) => { setUser(data); setSaved('profile'); setTimeout(() => setSaved(null), 2000) },
  })

  const saveWorkspace = useMutation({
    mutationFn: () => workspaceApi.update(workspace!.id, wsForm),
    onSuccess: ({ data }) => { setWorkspace(data); setSaved('workspace'); setTimeout(() => setSaved(null), 2000) },
  })

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-slate-400 text-sm mt-1">Manage your account and workspace preferences</p>
      </div>

      <Section title="Profile" icon={User}>
        <div className="space-y-4 max-w-md">
          <div>
            <label className="block text-sm text-slate-300 mb-1.5">Full Name</label>
            <input value={profileForm.full_name} onChange={e => setProfileForm(f => ({ ...f, full_name: e.target.value }))}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-blue-500 text-sm" />
          </div>
          <div>
            <label className="block text-sm text-slate-300 mb-1.5">Email</label>
            <input value={user?.email} disabled
              className="w-full px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-800 text-slate-500 text-sm cursor-not-allowed" />
          </div>
          <button onClick={() => saveProfile.mutate()} disabled={saveProfile.isPending}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium transition disabled:opacity-50">
            {saved === 'profile' ? <><Check size={14} /> Saved!</> : 'Save Profile'}
          </button>
        </div>
      </Section>

      <Section title="Workspace" icon={Building2}>
        <div className="space-y-4 max-w-md">
          <div>
            <label className="block text-sm text-slate-300 mb-1.5">Workspace Name</label>
            <input value={wsForm.name} onChange={e => setWsForm(f => ({ ...f, name: e.target.value }))}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-blue-500 text-sm" />
          </div>
          <div>
            <label className="block text-sm text-slate-300 mb-1.5">Website</label>
            <input value={wsForm.website} onChange={e => setWsForm(f => ({ ...f, website: e.target.value }))}
              placeholder="https://yourcompany.com"
              className="w-full px-4 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 text-sm" />
          </div>
          <div>
            <label className="block text-sm text-slate-300 mb-1.5">Industry</label>
            <input value={wsForm.industry} onChange={e => setWsForm(f => ({ ...f, industry: e.target.value }))}
              placeholder="SaaS, E-commerce, Healthcare..."
              className="w-full px-4 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 text-sm" />
          </div>
          <button onClick={() => saveWorkspace.mutate()} disabled={saveWorkspace.isPending || !workspace}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium transition disabled:opacity-50">
            {saved === 'workspace' ? <><Check size={14} /> Saved!</> : 'Save Workspace'}
          </button>
        </div>
      </Section>

      <Section title="Subscription" icon={Shield}>
        <div className="grid grid-cols-3 gap-4 max-w-2xl">
          {[
            { name: 'Free', price: '$0', features: ['50 leads/month', '100 emails/month', '1 workspace', 'Basic analytics'] },
            { name: 'Pro', price: '$49', features: ['2,000 leads/month', '5,000 emails/month', '5 workspaces', 'Advanced analytics', 'Priority support'] },
            { name: 'Enterprise', price: '$199', features: ['Unlimited leads', 'Unlimited emails', 'Unlimited workspaces', 'Custom AI models', 'Dedicated support'] },
          ].map(plan => (
            <div key={plan.name} className={`border rounded-xl p-4 ${plan.name === 'Pro' ? 'border-blue-500 bg-blue-500/5' : 'border-slate-700'}`}>
              <div className="text-white font-semibold">{plan.name}</div>
              <div className="text-2xl font-bold text-white mt-1">{plan.price}<span className="text-sm text-slate-400">/mo</span></div>
              <ul className="mt-3 space-y-1.5">
                {plan.features.map(f => (
                  <li key={f} className="text-slate-400 text-xs flex items-center gap-1.5">
                    <Check size={10} className="text-emerald-400 flex-shrink-0" /> {f}
                  </li>
                ))}
              </ul>
              <button className={`w-full mt-4 py-2 rounded-lg text-xs font-medium transition ${plan.name === 'Pro' ? 'bg-blue-600 hover:bg-blue-500 text-white' : 'border border-slate-700 text-slate-400 hover:border-slate-600'}`}>
                {plan.name === 'Free' ? 'Current Plan' : `Upgrade to ${plan.name}`}
              </button>
            </div>
          ))}
        </div>
      </Section>
    </div>
  )
}
