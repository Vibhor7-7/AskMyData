"use client"

import { motion, AnimatePresence } from "framer-motion"
import { Bot, User, ChevronDown, ChevronUp, Sparkles, Search, Loader2 } from "lucide-react"
import { useState, useEffect, useRef } from "react"

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

const LOADING_STAGES = [
  { message: "Understanding your question...", Icon: Loader2, spin: true },
  { message: "Searching through your data...", Icon: Search, spin: false },
  { message: "Generating your answer...", Icon: Sparkles, spin: true },
]

// How long to spend on each stage before advancing (ms)
const STAGE_DURATIONS = [800, 1400]

export function ChatMessages({ messages, isLoading }: ChatMessagesProps) {
  const [stageIndex, setStageIndex] = useState(0)
  const timersRef = useRef<ReturnType<typeof setTimeout>[]>([])

  useEffect(() => {
    timersRef.current.forEach(clearTimeout)
    timersRef.current = []

    if (isLoading) {
      setStageIndex(0)
      let elapsed = 0
      STAGE_DURATIONS.forEach((duration, i) => {
        elapsed += duration
        const t = setTimeout(() => setStageIndex(i + 1), elapsed)
        timersRef.current.push(t)
      })
    } else {
      setStageIndex(0)
    }

    return () => timersRef.current.forEach(clearTimeout)
  }, [isLoading])

  const currentStage = LOADING_STAGES[Math.min(stageIndex, LOADING_STAGES.length - 1)]

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
            <div className="rounded-2xl p-4 bg-gradient-to-br from-emerald-500/10 to-blue-500/10 border border-emerald-500/20 min-w-[220px]">
              <AnimatePresence mode="wait">
                <motion.div
                  key={stageIndex}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -6 }}
                  transition={{ duration: 0.2 }}
                  className="flex items-center gap-2"
                >
                  <motion.div
                    animate={currentStage.spin ? { rotate: 360 } : {}}
                    transition={{ duration: 1.5, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
                  >
                    <currentStage.Icon className="w-5 h-5 text-emerald-500 flex-shrink-0" />
                  </motion.div>
                  <span className="text-muted-foreground text-sm">{currentStage.message}</span>
                </motion.div>
              </AnimatePresence>
              {/* Stage dots */}
              <div className="flex gap-1 mt-2.5">
                {LOADING_STAGES.map((_, i) => (
                  <motion.div
                    key={i}
                    className="h-1 rounded-full bg-emerald-500"
                    animate={{ opacity: i <= stageIndex ? 1 : 0.2 }}
                    transition={{ duration: 0.3 }}
                    style={{ width: `${100 / LOADING_STAGES.length}%` }}
                  />
                ))}
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
