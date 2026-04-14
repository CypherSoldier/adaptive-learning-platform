import { Brain } from "lucide-react"

export function Footer() {
  return (
    <footer className="border-t border-border bg-background px-6 py-10">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 md:flex-row">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-full border border-primary/40 text-primary">
            <Brain className="h-3.5 w-3.5" />
          </div>
          <span className="text-sm font-semibold text-foreground">AdaptLearn</span>
        </div>
        <p className="text-xs text-muted-foreground">
          Built to help you master programming, one question at a time.
        </p>
      </div>
    </footer>
  )
}
