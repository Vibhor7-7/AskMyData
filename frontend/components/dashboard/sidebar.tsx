"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { motion } from "framer-motion"
import { Database, LayoutDashboard, Upload, MessageSquare, FolderOpen, LogOut, Settings } from "lucide-react"
import { cn } from "@/lib/utils"

const navItems = [
  { href: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/upload", icon: Upload, label: "Upload" },
  { href: "/chat", icon: MessageSquare, label: "Chat" },
  { href: "/files", icon: FolderOpen, label: "My Files" },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 glass-strong border-r border-border/50 flex flex-col z-40">
      {/* Logo */}
      <Link href="/dashboard" className="flex items-center gap-2 p-6 border-b border-border/50">
        <div className="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center">
          <Database className="w-5 h-5 text-primary-foreground" />
        </div>
        <span className="text-xl font-bold gradient-text">AskMyData</span>
      </Link>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    "relative flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all",
                    isActive
                      ? "text-primary-foreground"
                      : "text-muted-foreground hover:text-foreground hover:bg-secondary/50",
                  )}
                >
                  {isActive && (
                    <motion.div
                      layoutId="activeNav"
                      className="absolute inset-0 gradient-bg rounded-xl"
                      initial={false}
                      transition={{ type: "spring", stiffness: 500, damping: 30 }}
                    />
                  )}
                  <item.icon className="w-5 h-5 relative z-10" />
                  <span className="relative z-10">{item.label}</span>
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* Bottom section */}
      <div className="p-4 border-t border-border/50 space-y-2">
        <Link
          href="/settings"
          className="flex items-center gap-3 px-4 py-3 rounded-xl text-muted-foreground hover:text-foreground hover:bg-secondary/50 font-medium transition-all"
        >
          <Settings className="w-5 h-5" />
          <span>Settings</span>
        </Link>
        <Link
          href="/"
          className="flex items-center gap-3 px-4 py-3 rounded-xl text-muted-foreground hover:text-destructive hover:bg-destructive/10 font-medium transition-all"
        >
          <LogOut className="w-5 h-5" />
          <span>Logout</span>
        </Link>
      </div>
    </aside>
  )
}
