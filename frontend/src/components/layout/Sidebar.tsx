'use client'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/auth'
import {
  LayoutDashboard, Users, Megaphone, BarChart2, Mail,
  Settings, LogOut, Bot, Search, ChevronDown, Building2, ShieldAlert
} from 'lucide-react'
import { useState } from 'react'

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/dashboard/leads', label: 'Leads', icon: Users },
  { href: '/dashboard/campaigns', label: 'Campaigns', icon: Megaphone },
  { href: '/dashboard/emails', label: 'Emails', icon: Mail },
  { href: '/dashboard/analytics', label: 'Analytics', icon: BarChart2 },
  { href: '/dashboard/agents', label: 'AI Agents', icon: Bot },
  { href: '/dashboard/search', label: 'Vector Search', icon: Search },
  { href: '/dashboard/settings', label: 'Settings', icon: Settings },
]

export default function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const { user, workspace, logout } = useAuthStore()
  const [collapsed, setCollapsed] = useState(false)

  const handleLogout = () => {
    logout()
    router.push('/auth/login')
  }

  return (
    <aside className={`flex flex-col h-full bg-slate-900 border-r border-slate-800 transition-all duration-300 ${collapsed ? 'w-16' : 'w-64'}`}>
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-slate-800">
        <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-sm flex-shrink-0">A</div>
        {!collapsed && <span className="text-white font-bold text-sm truncate">AI Sales Agent</span>}
      </div>

      {/* Workspace Selector */}
      {!collapsed && workspace && (
        <div className="px-3 py-3 border-b border-slate-800">
          <div className="flex items-center gap-2 px-2 py-2 rounded-lg bg-slate-800 cursor-pointer hover:bg-slate-700 transition">
            <Building2 size={14} className="text-slate-400 flex-shrink-0" />
            <span className="text-slate-300 text-xs truncate flex-1">{workspace.name}</span>
            <ChevronDown size={12} className="text-slate-400" />
          </div>
        </div>
      )}

      {/* Nav */}
      <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || (href !== '/dashboard' && pathname.startsWith(href))
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all group ${
                active
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <Icon size={18} className="flex-shrink-0" />
              {!collapsed && <span>{label}</span>}
            </Link>
          )
        })}

        {/* Admin link for superusers */}
        {user?.is_superuser && (
          <>
            {!collapsed && <div className="px-3 pt-4 pb-1 text-xs font-medium text-slate-600 uppercase tracking-wider">Admin</div>}
            <Link
              href="/dashboard/admin"
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                pathname.startsWith('/dashboard/admin')
                  ? 'bg-red-600 text-white'
                  : 'text-red-400 hover:text-red-300 hover:bg-red-900/20'
              }`}
            >
              <ShieldAlert size={18} className="flex-shrink-0" />
              {!collapsed && <span>Admin Panel</span>}
            </Link>
          </>
        )}
      </nav>

      {/* User */}
      <div className="border-t border-slate-800 p-3">
        {!collapsed && user && (
          <div className="flex items-center gap-2 px-2 py-2 mb-2">
            <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
              {user.full_name?.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white text-xs font-medium truncate">{user.full_name}</p>
              <p className="text-slate-500 text-xs truncate">{user.email}</p>
            </div>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 text-sm w-full transition"
        >
          <LogOut size={16} />
          {!collapsed && 'Sign out'}
        </button>
      </div>
    </aside>
  )
}
