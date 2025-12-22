"use client"

import { motion } from "framer-motion"
import Link from "next/link"
import { Database } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/theme-toggle"

export function Navbar() {
  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="fixed top-0 left-0 right-0 z-50"
    >
      <nav className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between glass rounded-2xl px-6 py-3">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center">
              <Database className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold gradient-text">AskMyData</span>
          </Link>

          <div className="flex items-center gap-3">
            <ThemeToggle />
            <Link href="/login">
              <Button variant="ghost" className="font-medium">
                Login
              </Button>
            </Link>
            <Link href="/register">
              <Button className="gradient-bg hover:gradient-bg-hover text-primary-foreground font-medium">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </nav>
    </motion.header>
  )
}
