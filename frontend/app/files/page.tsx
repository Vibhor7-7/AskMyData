import { DashboardHeader } from "@/components/dashboard/header"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { FileText, MessageSquare, Trash2, Download } from "lucide-react"
import Link from "next/link"

const files = [
  {
    name: "sales_data.csv",
    type: "CSV",
    size: "2.4 MB",
    rows: 8547,
    columns: 12,
    uploadedAt: "2 hours ago",
  },
  {
    name: "customer_feedback.json",
    type: "JSON",
    size: "1.1 MB",
    rows: 3256,
    columns: 8,
    uploadedAt: "5 hours ago",
  },
  {
    name: "marketing_calendar.ics",
    type: "iCal",
    size: "45 KB",
    rows: null,
    columns: null,
    uploadedAt: "2 days ago",
  },
  {
    name: "inventory_report.pdf",
    type: "PDF",
    size: "856 KB",
    rows: null,
    columns: null,
    uploadedAt: "1 week ago",
  },
]

export default function FilesPage() {
  return (
    <div>
      <DashboardHeader title="My Files" subtitle="Manage your uploaded data files" />

      <div className="grid gap-4">
        {files.map((file) => (
          <Card key={file.name} className="border-border/50 bg-card/50 backdrop-blur-sm hover:shadow-lg transition-all">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-emerald-500/20 to-blue-500/20 flex items-center justify-center">
                    <FileText className="w-7 h-7 text-emerald-500" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">{file.name}</h3>
                    <div className="flex items-center gap-3 text-sm text-muted-foreground mt-1">
                      <span className="px-2 py-0.5 rounded-md bg-secondary">{file.type}</span>
                      <span>{file.size}</span>
                      {file.rows && <span>{file.rows.toLocaleString()} rows</span>}
                      {file.columns && <span>{file.columns} columns</span>}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground mr-4">{file.uploadedAt}</span>
                  <Link href="/chat">
                    <Button variant="outline" size="sm" className="gap-2 bg-transparent">
                      <MessageSquare className="w-4 h-4" />
                      Chat
                    </Button>
                  </Link>
                  <Button variant="outline" size="sm" className="gap-2 bg-transparent">
                    <Download className="w-4 h-4" />
                    Download
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-destructive hover:text-destructive hover:bg-destructive/10 bg-transparent"
                  >
                    <Trash2 className="w-4 h-4" />
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
