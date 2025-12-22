"use client"

import { motion } from "framer-motion"
import { Upload, MessageSquare, Zap, Shield, FileText, Calendar, FileJson } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

const features = [
  {
    icon: Upload,
    title: "Upload Any Format",
    description: "Support for CSV, JSON, PDF, and iCal files. Simply drag and drop to get started.",
    gradient: "from-emerald-500 to-emerald-600",
  },
  {
    icon: MessageSquare,
    title: "Natural Language Queries",
    description: "Ask questions in plain English. Our AI understands context and delivers precise answers.",
    gradient: "from-emerald-500 to-blue-500",
  },
  {
    icon: Zap,
    title: "Instant Insights",
    description: "Get answers in seconds with context-aware responses and relevant data snippets.",
    gradient: "from-blue-500 to-blue-600",
  },
  {
    icon: Shield,
    title: "Secure & Private",
    description: "Your data stays yours. Enterprise-grade security with end-to-end encryption.",
    gradient: "from-blue-600 to-indigo-600",
  },
]

const fileTypes = [
  { icon: FileText, label: "CSV", color: "text-emerald-500" },
  { icon: FileJson, label: "JSON", color: "text-blue-500" },
  { icon: FileText, label: "PDF", color: "text-rose-500" },
  { icon: Calendar, label: "iCal", color: "text-amber-500" },
]

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
    },
  },
}

export function FeaturesSection() {
  return (
    <section className="py-24 relative">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl font-bold mb-4 text-balance">
            Everything you need to <span className="gradient-text">analyze your data</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto text-pretty">
            Powerful features designed to help you extract meaningful insights from your data
          </p>
        </motion.div>

        {/* Supported File Types */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="flex justify-center gap-4 mb-16"
        >
          {fileTypes.map((type) => (
            <div key={type.label} className="flex items-center gap-2 px-4 py-2 rounded-full glass">
              <type.icon className={`w-5 h-5 ${type.color}`} />
              <span className="font-medium">{type.label}</span>
            </div>
          ))}
        </motion.div>

        {/* Feature Cards */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid md:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          {features.map((feature) => (
            <motion.div key={feature.title} variants={itemVariants}>
              <Card className="relative overflow-hidden h-full group hover:shadow-lg transition-all duration-300 border-border/50 bg-card/50 backdrop-blur-sm">
                <div
                  className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-300`}
                />
                <CardContent className="p-6 relative">
                  <div
                    className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-4`}
                  >
                    <feature.icon className="w-6 h-6 text-primary-foreground" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                  <p className="text-muted-foreground text-sm leading-relaxed">{feature.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
