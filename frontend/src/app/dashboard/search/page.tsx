'use client'
import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { searchApi } from '@/lib/api'
import { useAuthStore } from '@/store/auth'
import { Search, Loader2, Database } from 'lucide-react'

type Collection = 'companies' | 'leads' | 'emails'

export default function SearchPage() {
  const { workspace } = useAuthStore()
  const [query, setQuery] = useState('')
  const [collection, setCollection] = useState<Collection>('leads')
  const [limit, setLimit] = useState(5)

  const search = useMutation({
    mutationFn: () => searchApi.vector(workspace!.id, { query, collection, limit }).then(r => r.data),
  })

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Vector Search</h1>
        <p className="text-slate-400 text-sm mt-1">Semantic search across your companies, leads, and emails using Qdrant</p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
        <div className="flex gap-3">
          {(['companies', 'leads', 'emails'] as Collection[]).map(c => (
            <button key={c} onClick={() => setCollection(c)}
              className={`px-4 py-2 rounded-xl text-sm font-medium border transition capitalize ${collection === c ? 'bg-blue-600 border-blue-600 text-white' : 'border-slate-700 text-slate-400 hover:border-slate-600'}`}>
              {c}
            </button>
          ))}
        </div>
        <div className="flex gap-3">
          <div className="relative flex-1">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && query && search.mutate()}
              placeholder={`Search ${collection} semantically...`}
              className="w-full pl-10 pr-4 py-3 rounded-xl bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 text-sm"
            />
          </div>
          <select value={limit} onChange={e => setLimit(Number(e.target.value))}
            className="px-3 py-3 rounded-xl bg-slate-800 border border-slate-700 text-white focus:outline-none text-sm">
            {[3, 5, 10, 15].map(n => <option key={n} value={n}>Top {n}</option>)}
          </select>
          <button onClick={() => search.mutate()} disabled={!query || search.isPending || !workspace}
            className="px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium transition disabled:opacity-50">
            {search.isPending ? <Loader2 size={16} className="animate-spin" /> : 'Search'}
          </button>
        </div>
      </div>

      {search.isPending && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="animate-spin text-blue-500 mr-3" size={20} />
          <span className="text-slate-400">Searching vector database…</span>
        </div>
      )}

      {search.data && (
        <div className="space-y-3">
          <p className="text-slate-400 text-sm">{search.data.length} results for &ldquo;{query}&rdquo;</p>
          {search.data.length === 0 ? (
            <div className="text-center py-10 bg-slate-900 border border-slate-800 rounded-xl">
              <Database size={28} className="mx-auto text-slate-600 mb-3" />
              <p className="text-slate-400">No results found</p>
            </div>
          ) : (
            search.data.map((result: any) => (
              <div key={result.id} className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs text-slate-500 font-mono">{result.id}</span>
                  <div className="flex items-center gap-1.5">
                    <div className="h-1.5 rounded-full bg-slate-700 w-20 overflow-hidden">
                      <div className="h-full bg-blue-500 rounded-full" style={{ width: `${result.score * 100}%` }} />
                    </div>
                    <span className="text-blue-400 text-xs font-medium">{(result.score * 100).toFixed(0)}%</span>
                  </div>
                </div>
                <pre className="text-slate-300 text-xs overflow-x-auto bg-slate-800 rounded-lg p-3">
                  {JSON.stringify(result.payload, null, 2)}
                </pre>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}
