"use client"

import { useSearchParams } from "next/navigation"
import { ChatInterface } from "@/components/chat/chat-interface"

export default function ChatPage() {
  const searchParams = useSearchParams()
  const fileId = searchParams.get('file_id') ? parseInt(searchParams.get('file_id')!) : undefined
  
  return <ChatInterface selectedFileId={fileId} />
}
