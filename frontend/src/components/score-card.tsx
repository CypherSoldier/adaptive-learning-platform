"use client"

import { Info } from "lucide-react"
import { Progress } from "@/components/ui/progress"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"

interface ScoreCardProps {
  label: string
  value: number
  maxValue?: number
  tooltip: string
  color: string
}

export function ScoreCard({
  label,
  value,
  maxValue = 10,
  tooltip,
  color,
}: ScoreCardProps) {
  const percentage = (value / maxValue) * 100

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center gap-1.5">
        <span className="text-sm text-muted-foreground">{label}</span>
        <Tooltip>
          <TooltipTrigger asChild>
            <button
              type="button"
              className="inline-flex items-center justify-center text-muted-foreground/70 transition-colors hover:text-muted-foreground"
              aria-label={`Info about ${label}`}
            >
              <Info className="h-3.5 w-3.5" />
            </button>
          </TooltipTrigger>
          <TooltipContent side="top" className="max-w-55">
            {tooltip}
          </TooltipContent>
        </Tooltip>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-2xl font-bold text-foreground" style={{ color }}>
          {value}
        </span>
        <span className="text-sm text-muted-foreground">/ {maxValue}</span>
      </div>
      <Progress
        value={percentage}
        className="h-2 bg-secondary"
        style={
          {
            "--progress-color": color,
          } as React.CSSProperties
        }
      />
    </div>
  )
}
