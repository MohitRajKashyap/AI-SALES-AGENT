'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/auth'
import Sidebar from '@/components/layout/Sidebar'
import { workspaceApi } from '@/lib/api'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, setWorkspaces, setWorkspace, workspace } = useAuthStore()
  const router = useRouter()

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/auth/login')
      return
    }
    if (!workspace) {
      workspaceApi.list().then(({ data }) => {
        if (data.length > 0) {
          setWorkspaces(data)
          setWorkspace(data[0])
        } else {
          router.push('/onboarding')
        }
      }).catch(() => router.push('/auth/login'))
    }
  }, [isAuthenticated])

  if (!isAuthenticated) return null

  return (
    <div className="flex h-screen bg-slate-950 overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  )
}
