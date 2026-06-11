import Link from 'next/link'
import { Bot, Users, Mail, BarChart2, Zap, Shield, ArrowRight, CheckCircle } from 'lucide-react'

const features = [
  { icon: Bot, title: 'Multi-Agent AI', desc: 'LangGraph orchestrates 6 specialized AI agents for end-to-end sales automation.' },
  { icon: Users, title: 'Smart Lead Generation', desc: 'AI analyzes your company, finds ideal prospects, and scores them automatically.' },
  { icon: Mail, title: 'Personalized Outreach', desc: 'Generate hyper-personalized cold emails tailored to each prospect\'s context.' },
  { icon: BarChart2, title: 'CRM Analytics', desc: 'Track open rates, replies, meetings booked and conversion across all campaigns.' },
  { icon: Zap, title: 'Auto Follow-Ups', desc: 'Intelligent Day 3/7/14 follow-up sequences that adapt based on engagement.' },
  { icon: Shield, title: 'Vector Search', desc: 'Semantic search with Qdrant to find similar leads and companies instantly.' },
]

const stats = [
  { value: '10x', label: 'Faster prospecting' },
  { value: '68%', label: 'Higher reply rates' },
  { value: '3.2x', label: 'More meetings booked' },
  { value: '6', label: 'AI agents in workflow' },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Nav */}
      <nav className="border-b border-slate-800/50 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center font-bold text-sm">A</div>
            <span className="font-bold text-lg">AI Sales Agent</span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/auth/login" className="text-slate-400 hover:text-white text-sm transition">Sign in</Link>
            <Link href="/auth/register" className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-xl text-sm font-medium transition">
              Get started free
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 py-24 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-medium mb-6">
          <Zap size={12} /> Powered by GPT-4o + LangGraph
        </div>
        <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
          Automate Your Entire
          <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-400">
            Sales Pipeline with AI
          </span>
        </h1>
        <p className="text-slate-400 text-xl max-w-2xl mx-auto mb-10 leading-relaxed">
          Six AI agents working together — analyze websites, find leads, score prospects,
          write personalized emails, and manage follow-ups automatically.
        </p>
        <div className="flex items-center justify-center gap-4">
          <Link href="/auth/register"
            className="flex items-center gap-2 px-6 py-3.5 bg-blue-600 hover:bg-blue-500 rounded-xl font-semibold transition">
            Start for free <ArrowRight size={18} />
          </Link>
          <Link href="/auth/login" className="px-6 py-3.5 border border-slate-700 hover:border-slate-600 rounded-xl text-slate-300 transition">
            Sign in
          </Link>
        </div>
      </section>

      {/* Stats */}
      <section className="border-y border-slate-800/50 py-12">
        <div className="max-w-4xl mx-auto px-6 grid grid-cols-4 gap-8 text-center">
          {stats.map(s => (
            <div key={s.label}>
              <div className="text-3xl font-bold text-white mb-1">{s.value}</div>
              <div className="text-slate-400 text-sm">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-6 py-20">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">Everything you need to close more deals</h2>
          <p className="text-slate-400 max-w-xl mx-auto">
            A complete AI-powered outbound sales platform built for modern B2B teams.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition">
              <div className="w-10 h-10 rounded-xl bg-blue-600/20 flex items-center justify-center mb-4">
                <Icon size={20} className="text-blue-400" />
              </div>
              <h3 className="text-white font-semibold mb-2">{title}</h3>
              <p className="text-slate-400 text-sm leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-4xl mx-auto px-6 py-16 text-center">
        <div className="bg-gradient-to-r from-blue-600/20 to-indigo-600/20 border border-blue-500/20 rounded-3xl p-12">
          <h2 className="text-3xl font-bold mb-4">Ready to automate your sales?</h2>
          <p className="text-slate-400 mb-8">Join teams using AI to book more meetings without the manual work.</p>
          <Link href="/auth/register"
            className="inline-flex items-center gap-2 px-8 py-4 bg-blue-600 hover:bg-blue-500 rounded-xl font-semibold text-lg transition">
            Get started free <ArrowRight size={20} />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800/50 py-8 text-center">
        <p className="text-slate-500 text-sm">
          © 2025 AI Sales Agent · Built by <span className="text-slate-400">Mohit Raj Kashyap</span> · B.Tech CSE (AI/ML)
        </p>
      </footer>
    </div>
  )
}
