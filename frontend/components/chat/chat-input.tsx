"use client"

import type React from "react"
import { useState } from "react"
import { motion } from "framer-motion"
import { Send, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"

interface ChatInputProps {
  onSend: (message: string) => void
  isLoading: boolean
}

const exampleQuestions = [
  "What was the total revenue in Q3?",
  "Show me top 5 products by sales",
  "Which region performed best?",
  "Calculate average profit margin",
]

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [input, setInput] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim() && !isLoading) {
      onSend(input.trim())
      setInput("")
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="border-t border-border/50 p-4 space-y-4">
      {/* Example Questions */}
      <div className="flex flex-wrap gap-2">
        {exampleQuestions.map((question) => (
          <motion.button
            key={question}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setInput(question)}
            className="px-3 py-1.5 rounded-full text-sm bg-secondary/50 hover:bg-secondary text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1.5"
          >
            <Sparkles className="w-3 h-3" />
            {question}
          </motion.button>
        ))}
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="flex gap-3">
        <div className="relative flex-1">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your data..."
            className="resize-none pr-4 min-h-[56px] max-h-32 bg-card/50 border-border/50 focus:border-emerald-500/50 transition-colors"
            rows={1}
          />
        </div>
        <Button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="gradient-bg hover:gradient-bg-hover text-primary-foreground h-14 px-6"
        >
          <Send className="w-5 h-5" />
          <span className="sr-only">Send message</span>
        </Button>
      </form>
    </div>
  )
}
