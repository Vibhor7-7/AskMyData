"use client"

import { motion } from "framer-motion"
import Link from "next/link"
import { Upload, FolderOpen, MessageSquare, Plus } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const actions = [
  {
    href: "/upload",
    icon: Upload,
    label: "Upload New File",
    description: "Add CSV, JSON, PDF, or iCal files",
    primary: true,
  },
  {
    href: "/files",
    icon: FolderOpen,
    label: "View My Files",
    description: "Browse your uploaded data",
    primary: false,
  },
  {
    href: "/chat",
    icon: MessageSquare,
    label: "Start Chatting",
    description: "Ask questions about your data",
    primary: false,
  },
]

export function QuickActions() {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
      <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Plus className="w-5 h-5 text-emerald-500" />
            Quick Actions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-4">
            {actions.map((action) => (
              <Link key={action.href} href={action.href}>
                <div
                  className={`p-4 rounded-xl border transition-all hover:shadow-md cursor-pointer ${
                    action.primary
                      ? "gradient-bg text-primary-foreground border-transparent hover:shadow-emerald-500/20"
                      : "bg-secondary/30 border-border/50 hover:bg-secondary/50"
                  }`}
                >
                  <action.icon
                    className={`w-6 h-6 mb-3 ${action.primary ? "text-primary-foreground" : "text-emerald-500"}`}
                  />
                  <h3 className="font-semibold mb-1">{action.label}</h3>
                  <p className={`text-sm ${action.primary ? "text-primary-foreground/80" : "text-muted-foreground"}`}>
                    {action.description}
                  </p>
                </div>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
