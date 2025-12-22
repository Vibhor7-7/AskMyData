"use client"

import { useState, useCallback } from "react"
import { FileContextPanel } from "./file-context-panel"
import { ChatMessages } from "./chat-messages"
import { ChatInput } from "./chat-input"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  context?: string[]
  timestamp: Date
}

const initialMessages: Message[] = [
  {
    id: "1",
    role: "assistant",
    content:
      "Hello! I've loaded your sales_data.csv file with 8,547 rows of sales data. I can help you analyze revenue trends, product performance, regional comparisons, and more. What would you like to know?",
    timestamp: new Date(),
  },
]

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [isLoading, setIsLoading] = useState(false)

  const handleSend = useCallback(async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    // Simulate AI response
    await new Promise((resolve) => setTimeout(resolve, 1500))

    const responses: Record<string, { content: string; context?: string[] }> = {
      "What was the total revenue in Q3?": {
        content:
          "Based on the sales data from July to September 2024, the total revenue in Q3 was **$342,567.89**. This represents a 12.3% increase compared to Q2 ($305,102.45). The top contributing products were:\n\n1. Product A: $89,234\n2. Product B: $67,890\n3. Product C: $54,321",
        context: [
          'SUM(total_revenue) WHERE date BETWEEN "2024-07-01" AND "2024-09-30"',
          "Compared with Q2: $305,102.45",
          "Top products ordered by total_revenue DESC LIMIT 3",
        ],
      },
      "Show me top 5 products by sales": {
        content:
          "Here are your top 5 products by total sales:\n\n1. **Premium Widget** - $156,789 (1,234 units)\n2. **Standard Gadget** - $123,456 (2,567 units)\n3. **Deluxe Module** - $98,765 (876 units)\n4. **Basic Component** - $87,654 (3,456 units)\n5. **Pro Accessory** - $76,543 (1,987 units)\n\nThe Premium Widget leads in revenue despite lower unit sales, indicating a higher profit margin product.",
        context: [
          "SELECT product_name, SUM(total_revenue), SUM(quantity) GROUP BY product_name ORDER BY SUM(total_revenue) DESC LIMIT 5",
        ],
      },
      "Which region performed best?": {
        content:
          "The **West Region** performed best with total revenue of **$456,789**, followed by:\n\n- East Region: $398,234 (13% below West)\n- Central Region: $312,456 (32% below West)\n- South Region: $287,123 (37% below West)\n\nThe West Region's success is driven primarily by strong Q3 performance and higher average order values ($234 vs $189 company average).",
        context: [
          "SELECT region, SUM(total_revenue) GROUP BY region ORDER BY SUM(total_revenue) DESC",
          "AVG(total_revenue/quantity) by region for unit price comparison",
        ],
      },
      default: {
        content: `I've analyzed your question about "${content}". Based on the sales data, I can see several interesting patterns. Let me break down the key findings for you.\n\nWould you like me to dive deeper into any specific aspect of this analysis?`,
        context: ["Query processed from sales_data.csv", "8,547 rows analyzed"],
      },
    }

    const response = responses[content] || responses.default

    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: response.content,
      context: response.context,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, assistantMessage])
    setIsLoading(false)
  }, [])

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-background">
      <FileContextPanel />
      <div className="flex-1 flex flex-col">
        <ChatMessages messages={messages} isLoading={isLoading} />
        <ChatInput onSend={handleSend} isLoading={isLoading} />
      </div>
    </div>
  )
}
