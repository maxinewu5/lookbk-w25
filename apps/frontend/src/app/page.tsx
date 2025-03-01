import { Button } from "@/components/ui/button"
import Link from "next/link"

export default function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <Link href="/dashboard">
        <Button size="lg">Go to Dashboard</Button>
      </Link>
    </div>
  )
}
