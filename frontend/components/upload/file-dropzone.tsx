"use client"

import type React from "react"
import { useState, useCallback } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Upload, FileText, FileJson, Calendar, File, X, CheckCircle, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Card, CardContent } from "@/components/ui/card"

const fileTypes = [
  { icon: FileText, label: "CSV", extension: ".csv", color: "text-emerald-500" },
  { icon: FileJson, label: "JSON", extension: ".json", color: "text-blue-500" },
  { icon: FileText, label: "PDF", extension: ".pdf", color: "text-rose-500" },
  { icon: Calendar, label: "iCal", extension: ".ics", color: "text-amber-500" },
]

interface FileInfo {
  name: string
  size: number
  type: string
  rows?: number
  columns?: number
}

export function FileDropzone() {
  const [isDragging, setIsDragging] = useState(false)
  const [file, setFile] = useState<FileInfo | null>(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [isProcessed, setIsProcessed] = useState(false)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      processFile(droppedFile)
    }
  }, [])

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      processFile(selectedFile)
    }
  }, [])

  const processFile = (selectedFile: File) => {
    setFile({
      name: selectedFile.name,
      size: selectedFile.size,
      type: selectedFile.type || getFileType(selectedFile.name),
    })
    setIsProcessed(false)
    setUploadProgress(0)
  }

  const getFileType = (name: string): string => {
    const extension = name.split(".").pop()?.toLowerCase()
    switch (extension) {
      case "csv":
        return "text/csv"
      case "json":
        return "application/json"
      case "pdf":
        return "application/pdf"
      case "ics":
        return "text/calendar"
      default:
        return "unknown"
    }
  }

  const formatSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + " B"
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB"
    return (bytes / 1048576).toFixed(1) + " MB"
  }

  const getFileIcon = (type: string) => {
    if (type.includes("csv") || type.includes("spreadsheet")) return FileText
    if (type.includes("json")) return FileJson
    if (type.includes("pdf")) return FileText
    if (type.includes("calendar")) return Calendar
    return File
  }

  const handleUpload = async () => {
    setIsUploading(true)
    // Simulate upload progress
    for (let i = 0; i <= 100; i += 10) {
      await new Promise((resolve) => setTimeout(resolve, 150))
      setUploadProgress(i)
    }
    setIsUploading(false)
    setIsProcessed(true)
    // Simulate file info after processing
    if (file) {
      setFile({
        ...file,
        rows: Math.floor(Math.random() * 10000) + 100,
        columns: Math.floor(Math.random() * 20) + 3,
      })
    }
  }

  const clearFile = () => {
    setFile(null)
    setUploadProgress(0)
    setIsProcessed(false)
  }

  const FileIcon = file ? getFileIcon(file.type) : Upload

  return (
    <div className="space-y-6">
      {/* Supported formats */}
      <div className="flex justify-center gap-4 mb-8">
        {fileTypes.map((type) => (
          <div key={type.label} className="flex items-center gap-2 px-4 py-2 rounded-full glass">
            <type.icon className={`w-5 h-5 ${type.color}`} />
            <span className="font-medium">{type.label}</span>
          </div>
        ))}
      </div>

      {/* Dropzone */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative"
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          accept=".csv,.json,.pdf,.ics"
          onChange={handleFileSelect}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
        />

        <div
          className={`relative p-[2px] rounded-2xl transition-all duration-300 ${
            isDragging ? "bg-gradient-to-r from-emerald-500 to-blue-500" : "bg-gradient-to-r from-border to-border"
          }`}
        >
          <div
            className={`relative rounded-2xl p-12 transition-all duration-300 ${
              isDragging ? "bg-emerald-500/5" : "bg-card/50 backdrop-blur-sm"
            }`}
          >
            <AnimatePresence mode="wait">
              {!file ? (
                <motion.div
                  key="empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="text-center"
                >
                  <div
                    className={`w-20 h-20 rounded-2xl mx-auto mb-6 flex items-center justify-center transition-all duration-300 ${
                      isDragging
                        ? "gradient-bg scale-110"
                        : "bg-gradient-to-br from-emerald-500/20 to-blue-500/20 border-2 border-dashed border-emerald-500/30"
                    }`}
                  >
                    <Upload
                      className={`w-10 h-10 transition-colors ${isDragging ? "text-primary-foreground" : "text-emerald-500"}`}
                    />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">
                    {isDragging ? "Drop your file here" : "Drag & drop your file"}
                  </h3>
                  <p className="text-muted-foreground mb-4">or click to browse from your computer</p>
                  <p className="text-sm text-muted-foreground">Supports CSV, JSON, PDF, and iCal files up to 50MB</p>
                </motion.div>
              ) : (
                <motion.div
                  key="file"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  className="text-center"
                >
                  <div className="relative inline-block">
                    <div className="w-20 h-20 rounded-2xl gradient-bg mx-auto mb-4 flex items-center justify-center">
                      <FileIcon className="w-10 h-10 text-primary-foreground" />
                    </div>
                    {!isUploading && (
                      <button
                        onClick={clearFile}
                        className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-destructive text-destructive-foreground flex items-center justify-center hover:bg-destructive/90 transition-colors z-20"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                  <h3 className="text-lg font-semibold mb-1">{file.name}</h3>
                  <p className="text-sm text-muted-foreground mb-4">{formatSize(file.size)}</p>

                  {/* Upload Progress */}
                  {isUploading && (
                    <div className="max-w-xs mx-auto mb-4">
                      <Progress value={uploadProgress} className="h-2" />
                      <p className="text-sm text-muted-foreground mt-2">Processing... {uploadProgress}%</p>
                    </div>
                  )}

                  {/* Processed File Info */}
                  {isProcessed && file.rows && file.columns && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex items-center justify-center gap-4 mt-4"
                    >
                      <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 text-emerald-500">
                        <CheckCircle className="w-4 h-4" />
                        <span className="text-sm font-medium">Processed</span>
                      </div>
                      <div className="px-4 py-2 rounded-full bg-secondary text-sm">
                        {file.rows.toLocaleString()} rows
                      </div>
                      <div className="px-4 py-2 rounded-full bg-secondary text-sm">{file.columns} columns</div>
                    </motion.div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </motion.div>

      {/* Action Button */}
      {file && !isProcessed && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex justify-center">
          <Button
            onClick={handleUpload}
            disabled={isUploading}
            className="gradient-bg hover:gradient-bg-hover text-primary-foreground px-8 py-6 text-lg font-semibold"
          >
            {isUploading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Upload className="w-5 h-5 mr-2" />
                Process File
              </>
            )}
          </Button>
        </motion.div>
      )}

      {/* Start Chatting Button */}
      {isProcessed && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex justify-center">
          <Button
            onClick={() => (window.location.href = "/chat")}
            className="gradient-bg hover:gradient-bg-hover text-primary-foreground px-8 py-6 text-lg font-semibold"
          >
            Start Asking Questions
          </Button>
        </motion.div>
      )}

      {/* Recent Uploads */}
      <Card className="border-border/50 bg-card/50 backdrop-blur-sm mt-8">
        <CardContent className="p-6">
          <h3 className="font-semibold mb-4">Recent Uploads</h3>
          <div className="space-y-3">
            {[
              { name: "sales_data.csv", size: "2.4 MB", date: "2 hours ago" },
              { name: "customer_feedback.json", size: "1.1 MB", date: "5 hours ago" },
              { name: "marketing_calendar.ics", size: "45 KB", date: "2 days ago" },
            ].map((item) => (
              <div
                key={item.name}
                className="flex items-center justify-between p-3 rounded-xl bg-secondary/20 hover:bg-secondary/30 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500/20 to-blue-500/20 flex items-center justify-center">
                    <FileText className="w-5 h-5 text-emerald-500" />
                  </div>
                  <div>
                    <p className="font-medium">{item.name}</p>
                    <p className="text-xs text-muted-foreground">{item.size}</p>
                  </div>
                </div>
                <span className="text-sm text-muted-foreground">{item.date}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
