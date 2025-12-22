"use client"

import { motion } from "framer-motion"
import { FileText, Database, Calendar, Hash, Columns, ChevronDown, ChevronUp } from "lucide-react"
import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const fileInfo = {
  name: "sales_data.csv",
  type: "CSV",
  size: "2.4 MB",
  rows: 8547,
  columns: 12,
  lastModified: "2 hours ago",
  columnNames: [
    "date",
    "product_id",
    "product_name",
    "category",
    "quantity",
    "unit_price",
    "total_revenue",
    "region",
    "salesperson",
    "customer_id",
    "discount",
    "profit_margin",
  ],
}

export function FileContextPanel() {
  const [showColumns, setShowColumns] = useState(false)

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
          {/* File Info */}
          <div className="p-4 rounded-xl bg-secondary/30">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500/20 to-blue-500/20 flex items-center justify-center">
                <FileText className="w-6 h-6 text-emerald-500" />
              </div>
              <div>
                <p className="font-semibold">{fileInfo.name}</p>
                <p className="text-sm text-muted-foreground">{fileInfo.type} File</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="flex items-center gap-2">
                <Hash className="w-4 h-4 text-muted-foreground" />
                <span className="text-muted-foreground">Rows:</span>
                <span className="font-medium">{fileInfo.rows.toLocaleString()}</span>
              </div>
              <div className="flex items-center gap-2">
                <Columns className="w-4 h-4 text-muted-foreground" />
                <span className="text-muted-foreground">Cols:</span>
                <span className="font-medium">{fileInfo.columns}</span>
              </div>
              <div className="flex items-center gap-2 col-span-2">
                <Calendar className="w-4 h-4 text-muted-foreground" />
                <span className="text-muted-foreground">Updated:</span>
                <span className="font-medium">{fileInfo.lastModified}</span>
              </div>
            </div>
          </div>

          {/* Column Names */}
          <div>
            <button
              onClick={() => setShowColumns(!showColumns)}
              className="flex items-center justify-between w-full p-3 rounded-xl bg-secondary/30 hover:bg-secondary/50 transition-colors"
            >
              <span className="font-medium">Column Names</span>
              {showColumns ? (
                <ChevronUp className="w-4 h-4 text-muted-foreground" />
              ) : (
                <ChevronDown className="w-4 h-4 text-muted-foreground" />
              )}
            </button>
            {showColumns && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-2 p-3 rounded-xl bg-secondary/20"
              >
                <div className="flex flex-wrap gap-2">
                  {fileInfo.columnNames.map((col) => (
                    <span
                      key={col}
                      className="px-2 py-1 text-xs rounded-md bg-emerald-500/10 text-emerald-500 font-mono"
                    >
                      {col}
                    </span>
                  ))}
                </div>
              </motion.div>
            )}
          </div>

          {/* Quick Stats */}
          <div className="p-4 rounded-xl bg-gradient-to-br from-emerald-500/10 to-blue-500/10 border border-emerald-500/20">
            <p className="text-sm font-medium mb-2">Data Summary</p>
            <div className="space-y-1 text-sm text-muted-foreground">
              <p>Total Revenue: $1.2M</p>
              <p>Unique Products: 156</p>
              <p>Date Range: Jan - Dec 2024</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
