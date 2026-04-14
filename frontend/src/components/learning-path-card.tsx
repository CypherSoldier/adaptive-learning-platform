import Link from "next/link"
import { Code, ArrowRight } from "lucide-react"
import { Progress } from "@/components/ui/progress"

interface LearningPathCardProps {
  title: string
  slug: string
  description: string
  level: string
  modules: number
  progress: number
  accentColor: string
  iconBg: string
  progressColor: string
}

export function LearningPathCard({
  title,
  slug,
  description,
  level,
  modules,
  progress,
  accentColor,
  iconBg,
  progressColor,
}: LearningPathCardProps) {
  return (
    <div
      className="group flex flex-col justify-between rounded-xl border border-border bg-card p-6 transition-colors hover:border-border/80"
      style={{ borderTopColor: accentColor, borderTopWidth: "2px" }}
    >
      <div>
        <div className="flex items-center justify-between">
          <div
            className="flex h-10 w-10 items-center justify-center rounded-lg"
            style={{ backgroundColor: iconBg }}
          >
            <Code className="h-5 w-5" style={{ color: accentColor }} />
          </div>
          <span
            className="rounded-full px-3 py-1 text-xs font-medium"
            style={{
              backgroundColor: `${accentColor}15`,
              color: accentColor,
            }}
          >
            {level}
          </span>
        </div>

        <h3 className="mt-5 text-xl font-semibold text-foreground">{title}</h3>
        <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{description}</p>
      </div>

      <div className="mt-6">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span>{modules} modules</span>
          <span className="text-border">&#8226;</span>
          <span>{progress}% complete</span>
        </div>

        <div className="mt-3">
          <Progress
            value={progress}
            className="h-1.5 bg-secondary"
            style={
              {
                "--progress-color": progressColor,
              } as React.CSSProperties
            }
          />
        </div>

        <Link
          href={`/learn/${slug}`}
          className="mt-5 inline-flex items-center gap-1.5 text-sm font-medium transition-colors"
          style={{ color: accentColor }}
        >
          Start Learning
          <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
        </Link>
      </div>
    </div>
  )
}
