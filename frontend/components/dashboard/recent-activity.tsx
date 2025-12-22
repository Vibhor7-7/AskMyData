"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { FileText, MessageSquare, Clock } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { api, type FileInfo, type ChatMessage } from "@/lib/api"

interface Activity {
  type: "question" | "upload"
  content: string
  file: string
  time: string
  timestamp: Date
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

export function RecentActivity() {
  const [activities, setActivities] = useState<Activity[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchActivities = async () => {
      try {
        const [filesResponse, historyResponse] = await Promise.all([
          api.files.list(),
          api.ask.getHistory(),
        ])

        const fileActivities: Activity[] = filesResponse.files.slice(0, 5).map((file: FileInfo) => ({
          type: "upload" as const,
          content: "Uploaded new file",
          file: file.original_filename,
          time: formatTimeAgo(file.upload_date),
          timestamp: new Date(file.upload_date),
        }))

        const questionActivities: Activity[] = historyResponse.history.slice(0, 5).map((chat: ChatMessage) => ({
          type: "question" as const,
          content: chat.question || "Asked a question",
          file: "Data file",
          time: formatTimeAgo(chat.timestamp),
          timestamp: new Date(chat.timestamp),
        }))

        const combined = [...fileActivities, ...questionActivities]
          .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
          .slice(0, 5)

        setActivities(combined)
      } catch (error) {
        console.error('Failed to fetch activities:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchActivities()
  }, [])

  if (isLoading) {
    return (
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm mt-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-blue-500" />
              Recent Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center text-muted-foreground py-8">Loading activities...</div>
          </CardContent>
        </Card>
      </motion.div>
    )
  }
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
      <Card className="border-border/50 bg-card/50 backdrop-blur-sm mt-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="w-5 h-5 text-blue-500" />
            Recent Activity
          </CardTitle>
        </CardHeader>
        <CardContent>
          {activities.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              No recent activity. Upload a file or ask a question to get started!
            </div>
          ) : (
            <div className="space-y-4">
              {activities.map((activity, index) => (
                <div
                  key={index}
                  className="flex items-start gap-4 p-3 rounded-xl bg-secondary/20 hover:bg-secondary/30 transition-colors"
                >
                  <div
                    className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                      activity.type === "question"
                        ? "bg-gradient-to-br from-emerald-500 to-blue-500"
                        : "bg-gradient-to-br from-blue-500 to-indigo-500"
                    }`}
                  >
                    {activity.type === "question" ? (
                      <MessageSquare className="w-5 h-5 text-primary-foreground" />
                    ) : (
                      <FileText className="w-5 h-5 text-primary-foreground" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{activity.content}</p>
                    <p className="text-sm text-muted-foreground">{activity.file}</p>
                  </div>
                  <span className="text-xs text-muted-foreground whitespace-nowrap">{activity.time}</span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
