'use client'
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { analyticsApi } from '@/lib/api'
import { useAuthStore } from '@/store/auth'
import {
  AreaChart, Area, BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts'
import { Loader2 } from 'lucide-react'

const tooltipStyle = {
  contentStyle: { background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8 },
  labelStyle: { color: '#94a3b8' },
  itemStyle: { color: '#e2e8f0' },
}

export default function AnalyticsPage() {
  const { workspace } = useAuthStore()
  const [range, setRange] = useState(30)

  const { data: daily = [], isLoading } = useQuery({
    queryKey: ['daily-analytics', workspace?.id, range],
    queryFn: () => analyticsApi.daily(workspace!.id, range).then(r => r.data),
    enabled: !!workspace,
  })

  const { data: campaigns = [] } = useQuery({
    queryKey: ['campaign-performance', workspace?.id],
    queryFn: () => analyticsApi.campaigns(workspace!.id).then(r => r.data),
    enabled: !!workspace,
  })

  const totalSent = daily.reduce((a: number, d: any) => a + d.emails_sent, 0)
  const totalReplies = daily.reduce((a: number, d: any) => a + d.replies, 0)
  const totalLeads = daily.reduce((a: number, d: any) => a + d.new_leads, 0)
  const avgOpenRate = campaigns.length ? (campaigns.reduce((a: number, c: any) => a + c.open_rate, 0) / campaigns.length).toFixed(1) : '0.0'

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Analytics</h1>
          <p className="text-slate-400 text-sm mt-1">Track your outreach performance</p>
        </div>
        <div className="flex gap-2">
          {[7, 14, 30, 90].map(d => (
            <button key={d} onClick={() => setRange(d)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition ${range === d ? 'bg-blue-600 border-blue-600 text-white' : 'border-slate-700 text-slate-400 hover:border-slate-600'}`}>
              {d}d
            </button>
          ))}
        </div>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: 'Emails Sent', value: totalSent },
          { label: 'Replies', value: totalReplies },
          { label: 'New Leads', value: totalLeads },
          { label: 'Avg Open Rate', value: `${avgOpenRate}%` },
        ].map(stat => (
          <div key={stat.label} className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-white">{stat.value}</div>
            <div className="text-slate-400 text-sm mt-1">{stat.label}</div>
          </div>
        ))}
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-16"><Loader2 className="animate-spin text-blue-500" size={24} /></div>
      ) : (
        <div className="space-y-6">
          {/* Email activity */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <h2 className="text-white font-semibold mb-4">Email Activity</h2>
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={daily}>
                <defs>
                  <linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="g2" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="g3" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#a855f7" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#a855f7" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} tickFormatter={v => v.slice(5)} />
                <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
                <Tooltip {...tooltipStyle} />
                <Legend />
                <Area type="monotone" dataKey="emails_sent" stroke="#3b82f6" fill="url(#g1)" name="Sent" />
                <Area type="monotone" dataKey="emails_opened" stroke="#a855f7" fill="url(#g3)" name="Opened" />
                <Area type="monotone" dataKey="replies" stroke="#10b981" fill="url(#g2)" name="Replies" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Lead growth */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <h2 className="text-white font-semibold mb-4">Lead Growth</h2>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={daily}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} tickFormatter={v => v.slice(5)} />
                  <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
                  <Tooltip {...tooltipStyle} />
                  <Bar dataKey="new_leads" fill="#6366f1" name="New Leads" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Campaign performance */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <h2 className="text-white font-semibold mb-4">Campaign Open & Reply Rates</h2>
              {campaigns.length === 0 ? (
                <div className="flex items-center justify-center h-48 text-slate-500 text-sm">No campaign data yet</div>
              ) : (
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={campaigns} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis type="number" tick={{ fill: '#64748b', fontSize: 11 }} unit="%" />
                    <YAxis dataKey="campaign_name" type="category" tick={{ fill: '#64748b', fontSize: 10 }} width={80} />
                    <Tooltip {...tooltipStyle} />
                    <Legend />
                    <Bar dataKey="open_rate" fill="#3b82f6" name="Open %" radius={[0, 3, 3, 0]} />
                    <Bar dataKey="reply_rate" fill="#10b981" name="Reply %" radius={[0, 3, 3, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
