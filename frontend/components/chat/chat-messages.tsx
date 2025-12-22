"use client"

import { motion, AnimatePresence } from "framer-motion"
import { Bot, User, ChevronDown, ChevronUp, Sparkles } from "lucide-react"
import { useState } from "react"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  context?: string[]
  timestamp: Date
}

interface ChatMessagesProps {
  messages: Message[]
  isLoading: boolean
}

export function ChatMessages({ messages, isLoading }: ChatMessagesProps) {
  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      <AnimatePresence initial={false}>
        {messages.map((message) => (
          <motion.div
            key={message.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div className={`flex gap-3 max-w-[80%] ${message.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
              {/* Avatar */}
              <div
                className={`w-10 h-10 rounded-xl flex-shrink-0 flex items-center justify-center ${
                  message.role === "user"
                    ? "bg-gradient-to-br from-blue-500 to-blue-600"
                    : "bg-gradient-to-br from-emerald-500 to-emerald-600"
                }`}
              >
                {message.role === "user" ? (
                  <User className="w-5 h-5 text-primary-foreground" />
                ) : (
                  <Bot className="w-5 h-5 text-primary-foreground" />
                )}
              </div>

              {/* Message Bubble */}
              <div
                className={`rounded-2xl p-4 ${
                  message.role === "user"
                    ? "bg-gradient-to-br from-blue-500 to-blue-600 text-primary-foreground"
                    : "bg-gradient-to-br from-emerald-500/10 to-blue-500/10 border border-emerald-500/20"
                }`}
              >
                <p className="leading-relaxed">{message.content}</p>

                {/* Context Snippets */}
                {message.context && message.context.length > 0 && <ContextSnippets context={message.context} />}
              </div>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>

      {/* Loading Indicator */}
      {isLoading && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="flex justify-start">
          <div className="flex gap-3 max-w-[80%]">
            <div className="w-10 h-10 rounded-xl flex-shrink-0 flex items-center justify-center bg-gradient-to-br from-emerald-500 to-emerald-600">
              <Bot className="w-5 h-5 text-primary-foreground" />
            </div>
            <div className="rounded-2xl p-4 bg-gradient-to-br from-emerald-500/10 to-blue-500/10 border border-emerald-500/20">
              <div className="flex items-center gap-2">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
                >
                  <Sparkles className="w-5 h-5 text-emerald-500" />
                </motion.div>
                <span className="text-muted-foreground">Analyzing your data...</span>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}

function ContextSnippets({ context }: { context: string[] }) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div className="mt-3 pt-3 border-t border-current/10">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-2 text-sm opacity-70 hover:opacity-100 transition-opacity"
      >
        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        <span>View source context ({context.length} snippets)</span>
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-2 space-y-2 overflow-hidden"
          >
            {context.map((snippet, index) => (
              <div key={index} className="p-2 rounded-lg bg-background/30 text-xs font-mono opacity-80">
                {snippet}
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
