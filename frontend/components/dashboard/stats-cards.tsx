"use client"

import { motion } from "framer-motion"
import { FileText, MessageSquare, Calendar, TrendingUp } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

const stats = [
  {
    label: "Files Uploaded",
    value: "12",
    change: "+3 this week",
    icon: FileText,
    gradient: "from-emerald-500 to-emerald-600",
  },
  {
    label: "Questions Asked",
    value: "47",
    change: "+12 this week",
    icon: MessageSquare,
    gradient: "from-emerald-500 to-blue-500",
  },
  {
    label: "Last Upload",
    value: "2 hours ago",
    change: "sales_data.csv",
    icon: Calendar,
    gradient: "from-blue-500 to-blue-600",
  },
  {
    label: "Insights Generated",
    value: "156",
    change: "+28 this month",
    icon: TrendingUp,
    gradient: "from-blue-600 to-indigo-600",
  },
]

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

export function StatsCards() {
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
