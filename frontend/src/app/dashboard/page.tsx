'use client'
import { useQuery } from '@tanstack/react-query'
import { analyticsApi } from '@/lib/api'
import { useAuthStore } from '@/store/auth'
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, AreaChart, Area
} from 'recharts'
import {
  Users, Mail, MessageSquare, Calendar, TrendingUp,
  Flame, Activity, Zap
} from 'lucide-react'
import type { DashboardMetrics, DailyAnalytics } from '@/types'

function MetricCard({
  label, value, icon: Icon, color, subtitle
}: {
  label: string; value: string | number; icon: any; color: string; subtitle?: string
}) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition">
      <div className="flex items-start justify-between mb-4">
        <div className={`w-10 h-10 rounded-lg ${color} flex items-center justify-center`}>
          <Icon size={20} className="text-white" />
        </div>
      </div>
      <div className="text-2xl font-bold text-white mb-1">{value}</div>
      <div className="text-slate-400 text-sm">{label}</div>
      {subtitle && <div className="text-slate-500 text-xs mt-1">{subtitle}</div>}
    </div>
  )
}

export default function DashboardPage() {
  const { workspace } = useAuthStore()

  const { data: metrics } = useQuery<DashboardMetrics>({
    queryKey: ['dashboard-metrics', workspace?.id],
    queryFn: () => analyticsApi.dashboard(workspace!.id).then(r => r.data),
    enabled: !!workspace,
    refetchInterval: 30000,
  })

  const { data: daily = [] } = useQuery<DailyAnalytics[]>({
    queryKey: ['daily-analytics', workspace?.id],
    queryFn: () => analyticsApi.daily(workspace!.id, 30).then(r => r.data),
    enabled: !!workspace,
  })

  const { data: campaigns = [] } = useQuery({
    queryKey: ['campaign-performance', workspace?.id],
    queryFn: () => analyticsApi.campaigns(workspace!.id).then(r => r.data),
    enabled: !!workspace,
  })

  const metricCards = [
    { label: 'Total Leads', value: metrics?.total_leads ?? 0, icon: Users, color: 'bg-blue-600', subtitle: `${metrics?.hot_leads ?? 0} hot, ${metrics?.warm_leads ?? 0} warm` },
    { label: 'Emails Sent', value: metrics?.emails_sent ?? 0, icon: Mail, color: 'bg-indigo-600' },
    { label: 'Replies', value: metrics?.replies ?? 0, icon: MessageSquare, color: 'bg-emerald-600' },
    { label: 'Meetings Booked', value: metrics?.meetings_booked ?? 0, icon: Calendar, color: 'bg-amber-600' },
    { label: 'Conversion Rate', value: `${metrics?.conversion_rate ?? 0}%`, icon: TrendingUp, color: 'bg-purple-600' },
    { label: 'Hot Leads', value: metrics?.hot_leads ?? 0, icon: Flame, color: 'bg-red-600' },
    { label: 'Active Campaigns', value: metrics?.active_campaigns ?? 0, icon: Activity, color: 'bg-cyan-600' },
    { label: 'Warm Leads', value: metrics?.warm_leads ?? 0, icon: Zap, color: 'bg-orange-600' },
  ]

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-slate-400 text-sm mt-1">
            {workspace?.name} — AI-powered sales pipeline
          </p>
        </div>
        <div className="text-slate-500 text-sm">
          {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
        </div>
      </div>

      {/* Metrics grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {metricCards.map(card => (
          <MetricCard key={card.label} {...card} />
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Email activity */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h2 className="text-white font-semibold mb-4">Email Activity (30 days)</h2>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={daily}>
              <defs>
                <linearGradient id="sentGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="replyGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} tickFormatter={v => v.slice(5)} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8 }}
                labelStyle={{ color: '#94a3b8' }}
                itemStyle={{ color: '#e2e8f0' }}
              />
              <Area type="monotone" dataKey="emails_sent" stroke="#3b82f6" fill="url(#sentGrad)" name="Sent" />
              <Area type="monotone" dataKey="replies" stroke="#10b981" fill="url(#replyGrad)" name="Replies" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Lead growth */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h2 className="text-white font-semibold mb-4">Lead Growth</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={daily}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} tickFormatter={v => v.slice(5)} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8 }}
                labelStyle={{ color: '#94a3b8' }}
                itemStyle={{ color: '#e2e8f0' }}
              />
              <Bar dataKey="new_leads" fill="#6366f1" name="New Leads" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Campaign performance */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 lg:col-span-2">
          <h2 className="text-white font-semibold mb-4">Campaign Performance</h2>
          {campaigns.length === 0 ? (
            <div className="text-slate-500 text-sm text-center py-8">No campaigns yet. Create your first campaign to see performance data.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-slate-400 border-b border-slate-800">
                    <th className="text-left pb-3 font-medium">Campaign</th>
                    <th className="text-right pb-3 font-medium">Emails Sent</th>
                    <th className="text-right pb-3 font-medium">Open Rate</th>
                    <th className="text-right pb-3 font-medium">Reply Rate</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {campaigns.map((c: any) => (
                    <tr key={c.campaign_id} className="text-slate-300">
                      <td className="py-3 font-medium">{c.campaign_name}</td>
                      <td className="py-3 text-right">{c.emails_sent}</td>
                      <td className="py-3 text-right">
                        <span className={`px-2 py-0.5 rounded-full text-xs ${c.open_rate > 30 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-700 text-slate-400'}`}>
                          {c.open_rate}%
                        </span>
                      </td>
                      <td className="py-3 text-right">
                        <span className={`px-2 py-0.5 rounded-full text-xs ${c.reply_rate > 10 ? 'bg-blue-500/20 text-blue-400' : 'bg-slate-700 text-slate-400'}`}>
                          {c.reply_rate}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
