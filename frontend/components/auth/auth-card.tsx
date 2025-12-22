"use client"

import type React from "react"
import { motion } from "framer-motion"
import Link from "next/link"
import { Database } from "lucide-react"

interface AuthCardProps {
  children: React.ReactNode
  title: string
  subtitle: string
}

export function AuthCard({ children, title, subtitle }: AuthCardProps) {
  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden px-4 py-12">
      {/* Background effects */}
      <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 via-background to-blue-500/10" />
      <div className="absolute top-1/3 left-1/4 w-80 h-80 bg-emerald-500/20 rounded-full blur-3xl" />
      <div className="absolute bottom-1/3 right-1/4 w-80 h-80 bg-blue-500/20 rounded-full blur-3xl" />

      <motion.div
        initial={{ opacity: 0, y: 20, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 w-full max-w-md"
      >
        {/* Logo */}
        <Link href="/" className="flex items-center justify-center gap-2 mb-8">
          <div className="w-12 h-12 rounded-xl gradient-bg flex items-center justify-center">
            <Database className="w-6 h-6 text-primary-foreground" />
          </div>
          <span className="text-2xl font-bold gradient-text">AskMyData</span>
        </Link>

        {/* Card with gradient border effect */}
        <div className="relative p-[1px] rounded-2xl bg-gradient-to-br from-emerald-500/50 via-blue-500/30 to-emerald-500/50">
          <div className="glass-strong rounded-2xl p-8">
            <div className="text-center mb-8">
              <h1 className="text-2xl font-bold mb-2">{title}</h1>
              <p className="text-muted-foreground">{subtitle}</p>
            </div>
            {children}
          </div>
        </div>
      </motion.div>
    </div>
  )
}
