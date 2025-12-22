import { DashboardHeader } from "@/components/dashboard/header"
import { FileDropzone } from "@/components/upload/file-dropzone"

export default function UploadPage() {
  return (
    <div>
      <DashboardHeader title="Upload Files" subtitle="Upload your data files to start asking questions" />
      <FileDropzone />
    </div>
  )
}
