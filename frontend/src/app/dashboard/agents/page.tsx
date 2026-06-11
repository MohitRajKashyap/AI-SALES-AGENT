'use client'
import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { agentApi, companyApi } from '@/lib/api'
import { useAuthStore } from '@/store/auth'
import { Bot, Loader2, CheckCircle, XCircle, Clock, Play, ChevronDown, ChevronRight } from 'lucide-react'
import type { AgentLog } from '@/types'

const agentLabels: Record<string, string> = {
  website_analyzer: 'Website Analyzer',
  lead_finder: 'Lead Finder',
  lead_scorer: 'Lead Scorer',
  email_generator: 'Email Generator',
  followup_planner: 'Follow-Up Planner',
  crm_analytics: 'CRM Analytics',
}

const agentColors: Record<string, string> = {
  website_analyzer: 'bg-cyan-500/20 text-cyan-400',
  lead_finder: 'bg-blue-500/20 text-blue-400',
  lead_scorer: 'bg-purple-500/20 text-purple-400',
  email_generator: 'bg-emerald-500/20 text-emerald-400',
  followup_planner: 'bg-amber-500/20 text-amber-400',
  crm_analytics: 'bg-indigo-500/20 text-indigo-400',
}

function LogRow({ log }: { log: AgentLog }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
      <div className="flex items-center gap-4 p-4 cursor-pointer hover:bg-slate-800/30 transition" onClick={() => setOpen(!open)}>
        <span className={`px-2 py-1 rounded-lg text-xs font-medium ${agentColors[log.agent_type] || 'bg-slate-500/20 text-slate-400'}`}>
          {agentLabels[log.agent_type] || log.agent_type}
        </span>
        <div className="flex-1">
          <span className="text-slate-300 text-sm">{new Date(log.created_at).toLocaleString()}</span>
        </div>
        {log.duration_seconds && (
          <span className="text-slate-500 text-xs">{log.duration_seconds.toFixed(1)}s</span>
        )}
        {log.tokens_used > 0 && (
          <span className="text-slate-500 text-xs">{log.tokens_used} tokens</span>
        )}
        {log.status === 'completed' && <CheckCircle size={16} className="text-emerald-400 flex-shrink-0" />}
        {log.status === 'failed' && <XCircle size={16} className="text-red-400 flex-shrink-0" />}
        {log.status === 'running' && <Loader2 size={16} className="text-blue-400 animate-spin flex-shrink-0" />}
        {open ? <ChevronDown size={14} className="text-slate-400" /> : <ChevronRight size={14} className="text-slate-400" />}
      </div>
      {open && (
        <div className="border-t border-slate-800 p-4 space-y-3">
          {log.error_message && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-red-400 text-xs font-mono">{log.error_message}</div>
          )}
          {log.output_data && (
            <div>
              <p className="text-slate-400 text-xs mb-2">Output</p>
              <pre className="bg-slate-800 rounded-lg p-3 text-slate-300 text-xs overflow-x-auto">
                {JSON.stringify(log.output_data, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function AgentsPage() {
  const { workspace } = useAuthStore()
  const [url, setUrl] = useState('')
  const [pipelineResult, setPipelineResult] = useState<any>(null)

  const { data: logs = [], refetch } = useQuery<AgentLog[]>({
    queryKey: ['agent-logs', workspace?.id],
    queryFn: () => agentApi.logs(workspace!.id).then(r => r.data),
    enabled: !!workspace,
    refetchInterval: 5000,
  })

  const runPipeline = useMutation({
    mutationFn: () => companyApi.runPipeline(workspace!.id, url),
    onSuccess: ({ data }) => {
      setPipelineResult(data)
      refetch()
    },
  })

  const workflowNodes = [
    { id: 1, label: 'Website Analyzer', desc: 'Crawl & extract business profile', color: 'border-cyan-500/30 bg-cyan-500/5' },
    { id: 2, label: 'Lead Finder', desc: 'Generate prospect list', color: 'border-blue-500/30 bg-blue-500/5' },
    { id: 3, label: 'Lead Scorer', desc: 'Score & qualify leads', color: 'border-purple-500/30 bg-purple-500/5' },
    { id: 4, label: 'Email Generator', desc: 'Personalized outreach emails', color: 'border-emerald-500/30 bg-emerald-500/5' },
    { id: 5, label: 'Follow-Up Planner', desc: 'Day 3/7/14 sequences', color: 'border-amber-500/30 bg-amber-500/5' },
    { id: 6, label: 'CRM Analytics', desc: 'Track & report performance', color: 'border-indigo-500/30 bg-indigo-500/5' },
  ]

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">AI Agents</h1>
        <p className="text-slate-400 text-sm mt-1">LangGraph multi-agent workflow for automated sales</p>
      </div>

      {/* Workflow visualization */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <h2 className="text-white font-semibold mb-5">Agent Workflow</h2>
        <div className="flex items-stretch gap-3 overflow-x-auto pb-2">
          {workflowNodes.map((node, i) => (
            <div key={node.id} className="flex items-center gap-3 flex-shrink-0">
              <div className={`border ${node.color} rounded-xl p-4 min-w-36 text-center`}>
                <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center mx-auto mb-2">
                  <Bot size={14} className="text-slate-300" />
                </div>
                <p className="text-white text-xs font-semibold">{node.label}</p>
                <p className="text-slate-500 text-xs mt-1">{node.desc}</p>
              </div>
              {i < workflowNodes.length - 1 && (
                <div className="text-slate-600 font-bold text-lg">→</div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Full pipeline runner */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <h2 className="text-white font-semibold mb-1">Run Full Pipeline</h2>
        <p className="text-slate-400 text-sm mb-4">Enter a company URL to run all 6 agents in sequence automatically</p>
        <div className="flex gap-3">
          <input
            value={url}
            onChange={e => setUrl(e.target.value)}
            placeholder="https://targetcompany.com"
            className="flex-1 px-4 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 text-sm"
          />
          <button
            onClick={() => runPipeline.mutate()}
            disabled={!url || runPipeline.isPending}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium transition disabled:opacity-50"
          >
            {runPipeline.isPending ? <Loader2 size={15} className="animate-spin" /> : <Play size={15} />}
            {runPipeline.isPending ? 'Running...' : 'Run Pipeline'}
          </button>
        </div>

        {pipelineResult && (
          <div className="mt-4 p-4 bg-slate-800 rounded-xl space-y-2 text-sm">
            <div className="flex items-center gap-2">
              {pipelineResult.status === 'completed'
                ? <CheckCircle size={16} className="text-emerald-400" />
                : <XCircle size={16} className="text-red-400" />}
              <span className="text-white font-medium capitalize">{pipelineResult.status}</span>
            </div>
            <p className="text-slate-400">Leads found: <span className="text-white">{pipelineResult.leads_found}</span></p>
            <p className="text-slate-400">Emails generated: <span className="text-white">{pipelineResult.emails_generated}</span></p>
            {pipelineResult.errors?.length > 0 && (
              <p className="text-red-400 text-xs">{pipelineResult.errors.join(', ')}</p>
            )}
          </div>
        )}
      </div>

      {/* Agent logs */}
      <div>
        <h2 className="text-white font-semibold mb-4">Agent Execution Logs</h2>
        {logs.length === 0 ? (
          <div className="text-center py-10 bg-slate-900 border border-slate-800 rounded-xl">
            <Clock size={28} className="mx-auto text-slate-600 mb-3" />
            <p className="text-slate-400">No agent runs yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {logs.map(log => <LogRow key={log.id} log={log} />)}
          </div>
        )}
      </div>
    </div>
  )
}
