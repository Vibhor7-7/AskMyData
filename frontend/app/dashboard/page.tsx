"use client"

import { useEffect, useState } from "react"
import { DashboardHeader } from "@/components/dashboard/header"
import { StatsCards } from "@/components/dashboard/stats-cards"
import { QuickActions } from "@/components/dashboard/quick-actions"
import { RecentActivity } from "@/components/dashboard/recent-activity"
import { api } from "@/lib/api"
import { useRouter } from "next/navigation"

export default function DashboardPage() {
  const router = useRouter()
  const [userName, setUserName] = useState<string>("")
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const user = await api.auth.getCurrentUser()
        setUserName(user.username)
      } catch (error) {
        console.error('Failed to fetch user:', error)
        router.push('/login')
      } finally {
        setIsLoading(false)
      }
    }
    fetchUser()
  }, [router])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    )
  }

  return (
    <div>
      <DashboardHeader title={`Welcome back, ${userName}!`} subtitle="Here's what's happening with your data" />
      <StatsCards />
      <QuickActions />
      <RecentActivity />
    </div>
  )
}
