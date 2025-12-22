"use client"

import { motion } from "framer-motion"
import { FileText, MessageSquare, Clock } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const activities = [
  {
    type: "question",
    content: "What was the total revenue in Q3?",
    file: "sales_data.csv",
    time: "2 hours ago",
  },
  {
    type: "upload",
    content: "Uploaded new file",
    file: "customer_feedback.json",
    time: "5 hours ago",
  },
  {
    type: "question",
    content: "Show me the top 5 products by sales",
    file: "sales_data.csv",
    time: "1 day ago",
  },
  {
    type: "upload",
    content: "Uploaded new file",
    file: "marketing_calendar.ical",
    time: "2 days ago",
  },
]

export function RecentActivity() {
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
        </CardContent>
      </Card>
    </motion.div>
  )
}
