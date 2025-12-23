"use client"

import { motion } from "framer-motion"
import { FileText, Database, Calendar, Hash, Columns, ChevronDown, ChevronUp, Loader2 } from "lucide-react"
import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { api, type FileInfo } from "@/lib/api"

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

interface FileContextPanelProps {
  selectedFileId?: number
}

export function FileContextPanel({ selectedFileId }: FileContextPanelProps) {
  const [showColumns, setShowColumns] = useState(false)
  const [fileInfo, setFileInfo] = useState<FileInfo | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchFileInfo = async () => {
      setIsLoading(true)
      try {
        if (selectedFileId) {
          // Fetch specific file by ID
          const file = await api.files.get(selectedFileId)
          setFileInfo(file.file)
        } else {
          // Fetch most recent file
          const response = await api.files.list()
          if (response.files.length > 0) {
            setFileInfo(response.files[0])
          }
        }
      } catch (error) {
        console.error('Failed to fetch file info:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchFileInfo()
  }, [selectedFileId])

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="w-80 flex-shrink-0 border-r border-border/50 h-full overflow-y-auto p-4"
    >
      <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <div className="w-8 h-8 rounded-lg gradient-bg flex items-center justify-center">
              <Database className="w-4 h-4 text-primary-foreground" />
            </div>
            File Context
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
            </div>
          ) : !fileInfo ? (
            <div className="text-center py-8">
              <FileText className="w-12 h-12 mx-auto text-muted-foreground mb-3" />
              <p className="text-sm text-muted-foreground">No files uploaded yet</p>
              <p className="text-xs text-muted-foreground mt-1">Upload a file to see context</p>
            </div>
          ) : (
            <>
              {/* File Info */}
              <div className="p-4 rounded-xl bg-secondary/30">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500/20 to-blue-500/20 flex items-center justify-center">
                    <FileText className="w-6 h-6 text-emerald-500" />
                  </div>
                  <div>
                    <p className="font-semibold">{fileInfo.original_filename}</p>
                    <p className="text-sm text-muted-foreground">{fileInfo.file_type.toUpperCase()} File</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div className="flex items-center gap-2">
                    <Hash className="w-4 h-4 text-muted-foreground" />
                    <span className="text-muted-foreground">Rows:</span>
                    <span className="font-medium">{fileInfo.num_rows.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Columns className="w-4 h-4 text-muted-foreground" />
                    <span className="text-muted-foreground">Cols:</span>
                    <span className="font-medium">{fileInfo.num_columns}</span>
                  </div>
                  <div className="flex items-center gap-2 col-span-2">
                    <Calendar className="w-4 h-4 text-muted-foreground" />
                    <span className="text-muted-foreground">Updated:</span>
                    <span className="font-medium">{formatTimeAgo(fileInfo.upload_date)}</span>
                  </div>
                  <div className="flex items-center gap-2 col-span-2">
                    <Database className="w-4 h-4 text-muted-foreground" />
                    <span className="text-muted-foreground">Size:</span>
                    <span className="font-medium">{formatFileSize(fileInfo.file_size)}</span>
                  </div>
                </div>
              </div>

              {/* Quick Stats */}
              <div className="p-4 rounded-xl bg-gradient-to-br from-emerald-500/10 to-blue-500/10 border border-emerald-500/20">
                <p className="text-sm font-medium mb-2">Data Summary</p>
                <div className="space-y-1 text-sm text-muted-foreground">
                  <p>Total Chunks: {fileInfo.num_chunks}</p>
                  <p>Collection: {fileInfo.collection_name}</p>
                  <p>Uploaded: {new Date(fileInfo.upload_date).toLocaleDateString()}</p>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
