"use client"

import { useState, useCallback, useEffect } from "react"
import { FileContextPanel } from "./file-context-panel"
import { ChatMessages } from "./chat-messages"
import { ChatInput } from "./chat-input"
import { useToast } from "@/hooks/use-toast"
import { api, type ChatMessage as ApiChatMessage } from "@/lib/api"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  context?: string[]
  timestamp: Date
}

interface ChatInterfaceProps {
  selectedFileId?: number
}

export function ChatInterface({ selectedFileId }: ChatInterfaceProps) {
  const { toast } = useToast()
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingHistory, setIsLoadingHistory] = useState(true)

  // Load chat history on mount
  useEffect(() => {
    const loadChatHistory = async () => {
      try {
        const history = await api.ask.getHistory()
        
        if (history.history && history.history.length > 0) {
          const loadedMessages: Message[] = history.history.map((msg: ApiChatMessage) => ({
            id: msg.chat_id.toString(),
            role: msg.question ? "user" : "assistant",
            content: msg.question || msg.answer || "",
            context: msg.context ? [msg.context] : undefined,
            timestamp: new Date(msg.timestamp),
          }))
          
          setMessages(loadedMessages)
        } else {
          // Show welcome message if no history
          setMessages([{
            id: "welcome",
            role: "assistant",
            content: "Hello! Upload a file and I can help you analyze it. Ask me anything about your data!",
            timestamp: new Date(),
          }])
        }
      } catch (error: any) {
        console.error('Failed to load chat history:', error)
        toast({
          title: "Could not load chat history",
          description: error.message || "Failed to load previous conversations",
          variant: "destructive",
        })
        setMessages([{
          id: "welcome",
          role: "assistant",
          content: "Hello! Upload a file and I can help you analyze it. Ask me anything about your data!",
          timestamp: new Date(),
        }])
      } finally {
        setIsLoadingHistory(false)
      }
    }
    
    loadChatHistory()
  }, [])

  const handleSend = useCallback(async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      // Call backend API with optional file_id
      const response = await api.ask.ask(content, selectedFileId)

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.answer,
        context: response.context ? [response.context] : undefined,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, aiMessage])
    } catch (error: any) {
      console.error('Failed to get answer:', error)
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `Sorry, I encountered an error: ${error.message || 'Failed to process your question'}. Please make sure you have uploaded a file first.`,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, errorMessage])
      
      toast({
        title: "Failed to get answer",
        description: error.message || "Please try again or upload a file first",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }, [toast])

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-background">
      <FileContextPanel selectedFileId={selectedFileId} />
      <div className="flex-1 flex flex-col">
        <ChatMessages messages={messages} isLoading={isLoading} />
        <ChatInput onSend={handleSend} isLoading={isLoading} />
      </div>
    </div>
  )
}
