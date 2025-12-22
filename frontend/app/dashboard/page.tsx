import { DashboardHeader } from "@/components/dashboard/header"
import { StatsCards } from "@/components/dashboard/stats-cards"
import { QuickActions } from "@/components/dashboard/quick-actions"
import { RecentActivity } from "@/components/dashboard/recent-activity"

export default function DashboardPage() {
  return (
    <div>
      <DashboardHeader title="Welcome back, John!" subtitle="Here's what's happening with your data" />
      <StatsCards />
      <QuickActions />
      <RecentActivity />
    </div>
  )
}
