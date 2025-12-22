import { AuthCard } from "@/components/auth/auth-card"
import { RegisterForm } from "@/components/auth/register-form"

export default function RegisterPage() {
  return (
    <AuthCard title="Create an account" subtitle="Get started with AskMyData today">
      <RegisterForm />
    </AuthCard>
  )
}
