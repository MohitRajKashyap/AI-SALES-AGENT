'use client'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { adminApi } from '@/lib/api'
import { useAuthStore } from '@/store/auth'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import {
  Users, Building2, Mail, Megaphone, BarChart2,
  UserX, UserCheck, ShieldAlert, Loader2
} from 'lucide-react'

function StatCard({ label, value, icon: Icon, color }: { label: string; value: number; icon: any; color: string }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <div className={`w-10 h-10 rounded-lg ${color} flex items-center justify-center mb-4`}>
        <Icon size={20} className="text-white" />
      </div>
      <div className="text-3xl font-bold text-white">{value.toLocaleString()}</div>
      <div className="text-slate-400 text-sm mt-1">{label}</div>
    </div>
  )
}

export default function AdminPage() {
  const { user } = useAuthStore()
  const router = useRouter()
  const qc = useQueryClient()

  useEffect(() => {
    if (user && !user.is_superuser) router.push('/dashboard')
  }, [user])

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: () => adminApi.stats().then(r => r.data),
    enabled: !!user?.is_superuser,
  })

  const { data: users = [], isLoading: usersLoading } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => adminApi.users().then(r => r.data),
    enabled: !!user?.is_superuser,
  })

  const deactivate = useMutation({
    mutationFn: (id: string) => adminApi.deactivateUser(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin-users'] }),
  })

  const activate = useMutation({
    mutationFn: (id: string) => adminApi.activateUser(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin-users'] }),
  })

  if (!user?.is_superuser) return null

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-red-600/20 flex items-center justify-center">
          <ShieldAlert size={18} className="text-red-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">Admin Panel</h1>
          <p className="text-slate-400 text-sm">Superuser access only</p>
        </div>
      </div>

      {/* Stats */}
      {statsLoading ? (
        <div className="flex items-center gap-2 text-slate-400">
          <Loader2 size={16} className="animate-spin" /> Loading stats…
        </div>
      ) : stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <StatCard label="Total Users" value={stats.total_users} icon={Users} color="bg-blue-600" />
          <StatCard label="Workspaces" value={stats.total_workspaces} icon={Building2} color="bg-indigo-600" />
          <StatCard label="Total Leads" value={stats.total_leads} icon={Users} color="bg-emerald-600" />
          <StatCard label="Emails" value={stats.total_emails} icon={Mail} color="bg-purple-600" />
          <StatCard label="Campaigns" value={stats.total_campaigns} icon={Megaphone} color="bg-amber-600" />
        </div>
      )}

      {/* Users table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between">
          <h2 className="text-white font-semibold">All Users</h2>
          <span className="text-slate-500 text-sm">{users.length} total</span>
        </div>

        {usersLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="animate-spin text-blue-500" size={22} />
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-slate-400 border-b border-slate-800">
                <th className="text-left px-5 py-3 font-medium">User</th>
                <th className="text-left px-5 py-3 font-medium">Role</th>
                <th className="text-left px-5 py-3 font-medium">Joined</th>
                <th className="text-center px-5 py-3 font-medium">Status</th>
                <th className="px-5 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {users.map((u: any) => (
                <tr key={u.id} className="hover:bg-slate-800/30 transition group">
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-blue-600/30 flex items-center justify-center text-blue-400 text-xs font-bold flex-shrink-0">
                        {u.full_name?.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <div className="text-white font-medium">{u.full_name}</div>
                        <div className="text-slate-500 text-xs">{u.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-0.5 rounded-full text-xs border ${
                        u.is_superuser
                          ? 'border-red-500/30 bg-red-500/10 text-red-400'
                          : 'border-slate-700 text-slate-400'
                      }`}>
                        {u.is_superuser ? 'superuser' : u.role}
                      </span>
                    </div>
                  </td>
                  <td className="px-5 py-4 text-slate-400">
                    {new Date(u.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-5 py-4 text-center">
                    <span className={`px-2 py-0.5 rounded-full text-xs ${
                      u.is_active
                        ? 'bg-emerald-500/10 text-emerald-400'
                        : 'bg-red-500/10 text-red-400'
                    }`}>
                      {u.is_active ? 'active' : 'inactive'}
                    </span>
                  </td>
                  <td className="px-5 py-4">
                    {u.id !== user?.id && (
                      <div className="flex justify-end opacity-0 group-hover:opacity-100 transition">
                        {u.is_active ? (
                          <button
                            onClick={() => deactivate.mutate(u.id)}
                            disabled={deactivate.isPending}
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-red-500/30 text-red-400 hover:bg-red-500/10 text-xs transition disabled:opacity-50"
                          >
                            <UserX size={12} /> Deactivate
                          </button>
                        ) : (
                          <button
                            onClick={() => activate.mutate(u.id)}
                            disabled={activate.isPending}
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10 text-xs transition disabled:opacity-50"
                          >
                            <UserCheck size={12} /> Activate
                          </button>
                        )}
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
