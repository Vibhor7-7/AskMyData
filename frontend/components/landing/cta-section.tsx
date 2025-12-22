"use client"

import { motion } from "framer-motion"
import Link from "next/link"
import { ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"

export function CTASection() {
  return (
    <section className="py-24 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/10 via-blue-500/10 to-emerald-500/10" />

      <div className="container mx-auto px-4 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="max-w-3xl mx-auto text-center"
        >
          <h2 className="text-3xl md:text-5xl font-bold mb-6 text-balance">Ready to unlock insights from your data?</h2>
          <p className="text-lg text-muted-foreground mb-8 text-pretty">
            Join thousands of users who are already making data-driven decisions with AskMyData.
          </p>
          <Link href="/register">
            <Button
              size="lg"
              className="gradient-bg hover:gradient-bg-hover text-primary-foreground px-8 py-6 text-lg font-semibold shadow-lg shadow-emerald-500/25 transition-all hover:shadow-xl hover:shadow-emerald-500/30"
            >
              Start Free Today
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </Link>
        </motion.div>
      </div>
    </section>
  )
}
