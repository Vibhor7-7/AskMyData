"use client"

import { useEffect, useState } from "react"
import { DashboardHeader } from "@/components/dashboard/header"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { FileText, MessageSquare, Trash2, Download, Loader2 } from "lucide-react"
import Link from "next/link"
import { api, type FileInfo } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000)
  
  if (seconds < 60) return 'Just now'
  if (seconds < 3600) return `${Math.floor(seconds / 60)} min ago`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`
  return `${Math.floor(seconds / 86400)} days ago`
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function FilesPage() {
  const { toast } = useToast()
  const [files, setFiles] = useState<FileInfo[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [deletingId, setDeletingId] = useState<number | null>(null)

  const fetchFiles = async () => {
    try {
      const response = await api.files.list()
      setFiles(response.files)
    } catch (error: any) {
      console.error('Failed to fetch files:', error)
      toast({
        title: "Failed to load files",
        description: error.message || "Could not load your files",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchFiles()
  }, [])

  const handleDelete = async (fileId: number, filename: string) => {
    if (!confirm(`Are you sure you want to delete ${filename}?`)) return

    setDeletingId(fileId)
    try {
      await api.files.delete(fileId)
      setFiles(files.filter(f => f.file_id !== fileId))
      toast({
        title: "File deleted",
        description: `${filename} has been deleted successfully`,
      })
    } catch (error: any) {
      console.error('Failed to delete file:', error)
      toast({
        title: "Failed to delete file",
        description: error.message || "Could not delete the file",
        variant: "destructive",
      })
    } finally {
      setDeletingId(null)
    }
  }

  if (isLoading) {
    return (
      <div>
        <DashboardHeader title="My Files" subtitle="Manage your uploaded data files" />
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    )
  }

  if (files.length === 0) {
    return (
      <div>
        <DashboardHeader title="My Files" subtitle="Manage your uploaded data files" />
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
          <CardContent className="p-12 text-center">
            <FileText className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-xl font-semibold mb-2">No files uploaded yet</h3>
            <p className="text-muted-foreground mb-6">Upload your first file to start analyzing your data</p>
            <Link href="/upload">
              <Button className="gradient-bg">Upload File</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div>
      <DashboardHeader title="My Files" subtitle="Manage your uploaded data files" />

      <div className="grid gap-4">
        {files.map((file) => (
          <Card key={file.file_id} className="border-border/50 bg-card/50 backdrop-blur-sm hover:shadow-lg transition-all">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-emerald-500/20 to-blue-500/20 flex items-center justify-center">
                    <FileText className="w-7 h-7 text-emerald-500" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">{file.original_filename}</h3>
                    <div className="flex items-center gap-3 text-sm text-muted-foreground mt-1">
                      <span className="px-2 py-0.5 rounded-md bg-secondary">{file.file_type.toUpperCase()}</span>
                      <span>{formatFileSize(file.file_size)}</span>
                      {file.num_rows > 0 && <span>{file.num_rows.toLocaleString()} rows</span>}
                      {file.num_columns > 0 && <span>{file.num_columns} columns</span>}
                      <span className="text-xs">{file.num_chunks} chunks</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground mr-4">{formatTimeAgo(file.upload_date)}</span>
                  <Link href="/chat">
                    <Button variant="outline" size="sm" className="gap-2 bg-transparent">
                      <MessageSquare className="w-4 h-4" />
                      Chat
                    </Button>
                  </Link>
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-destructive hover:text-destructive hover:bg-destructive/10 bg-transparent"
                    onClick={() => handleDelete(file.file_id, file.original_filename)}
                    disabled={deletingId === file.file_id}
                  >
                    {deletingId === file.file_id ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Trash2 className="w-4 h-4" />
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
