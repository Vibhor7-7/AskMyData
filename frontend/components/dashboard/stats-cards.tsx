"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { FileText, MessageSquare, Calendar, TrendingUp } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { api } from "@/lib/api"

interface Stats {
  label: string
  value: string
  change: string
  icon: any
  gradient: string
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
}

function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000)
  
  if (seconds < 60) return 'Just now'
  if (seconds < 3600) return `${Math.floor(seconds / 60)} min ago`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`
  return `${Math.floor(seconds / 86400)} days ago`
}

export function StatsCards() {
  const [stats, setStats] = useState<Stats[]>([
    {
      label: "Files Uploaded",
      value: "0",
      change: "Loading...",
      icon: FileText,
      gradient: "from-emerald-500 to-emerald-600",
    },
    {
      label: "Questions Asked",
      value: "0",
      change: "Loading...",
      icon: MessageSquare,
      gradient: "from-emerald-500 to-blue-500",
    },
    {
      label: "Last Upload",
      value: "N/A",
      change: "No files yet",
      icon: Calendar,
      gradient: "from-blue-500 to-blue-600",
    },
    {
      label: "Insights Generated",
      value: "0",
      change: "Total questions",
      icon: TrendingUp,
      gradient: "from-blue-600 to-indigo-600",
    },
  ])

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [filesResponse, historyResponse] = await Promise.all([
          api.files.list(),
          api.ask.getHistory(),
        ])

        const files = filesResponse.files
        const history = historyResponse.history

        const lastFile = files.length > 0 ? files[0] : null

        setStats([
          {
            label: "Files Uploaded",
            value: files.length.toString(),
            change: files.length > 0 ? `${files.length} total files` : "No files yet",
            icon: FileText,
            gradient: "from-emerald-500 to-emerald-600",
          },
          {
            label: "Questions Asked",
            value: history.length.toString(),
            change: history.length > 0 ? `${history.length} total questions` : "No questions yet",
            icon: MessageSquare,
            gradient: "from-emerald-500 to-blue-500",
          },
          {
            label: "Last Upload",
            value: lastFile ? formatTimeAgo(lastFile.upload_date) : "N/A",
            change: lastFile ? lastFile.original_filename : "No files yet",
            icon: Calendar,
            gradient: "from-blue-500 to-blue-600",
          },
          {
            label: "Insights Generated",
            value: history.length.toString(),
            change: `From ${files.length} files`,
            icon: TrendingUp,
            gradient: "from-blue-600 to-indigo-600",
          },
        ])
      } catch (error) {
        console.error('Failed to fetch stats:', error)
      }
    }

    fetchStats()
  }, [])

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
    >
      {stats.map((stat) => (
        <motion.div key={stat.label} variants={itemVariants}>
          <Card className="relative overflow-hidden border-border/50 bg-card/50 backdrop-blur-sm hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">{stat.label}</p>
                  <p className="text-2xl font-bold">{stat.value}</p>
                  <p className="text-xs text-muted-foreground mt-1">{stat.change}</p>
                </div>
                <div
                  className={`w-10 h-10 rounded-xl bg-gradient-to-br ${stat.gradient} flex items-center justify-center`}
                >
                  <stat.icon className="w-5 h-5 text-primary-foreground" />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </motion.div>
  )
}
