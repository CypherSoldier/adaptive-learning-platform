import type { LucideIcon } from "lucide-react"

interface FeatureCardProps {
  icon: LucideIcon
  title: string
  description: string
  accentColor: string
}

export function FeatureCard({
  icon: Icon,
  title,
  description,
  accentColor,
}: FeatureCardProps) {
  return (
    <div className="rounded-xl border border-border bg-card p-6">
      <div
        className="flex h-10 w-10 items-center justify-center rounded-lg"
        style={{ backgroundColor: `${accentColor}15` }}
      >
        <Icon className="h-5 w-5" style={{ color: accentColor }} />
      </div>
      <h3 className="mt-4 text-sm font-semibold text-foreground">{title}</h3>
      <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">
        {description}
      </p>
    </div>
  )
}
