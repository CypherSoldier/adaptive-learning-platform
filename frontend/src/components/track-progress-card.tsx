"use client"

import { Code } from "lucide-react"
import { ScoreCard } from "@/components/score-card"

interface TrackProgressCardProps {
  title: string
  skillScore: number
  confidenceScore: number
  //questionsAnswered: number
  accentColor: string
  iconBg: string
}

export function TrackProgressCard({
  title,
  skillScore,
  confidenceScore,
  //questionsAnswered,
  accentColor,
  iconBg,
}: TrackProgressCardProps) {
  return (
    <div
      className="rounded-xl border border-border bg-card p-6"
      style={{ borderTopColor: accentColor, borderTopWidth: "2px" }}
    >
      <div className="flex items-center gap-3">
        <div
          className="flex h-10 w-10 items-center justify-center rounded-lg"
          style={{ backgroundColor: iconBg }}
        >
          <Code className="h-5 w-5" style={{ color: accentColor }} />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-foreground">{title}</h3>
          <p className="text-xs text-muted-foreground">
            000 questions answered
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-6 sm:grid-cols-2">
        <ScoreCard
          label="Skill Score"
          value={skillScore}
          tooltip="Measures your overall proficiency based on correct answers and question difficulty. Higher scores unlock harder questions."
          color={accentColor}
        />
        <ScoreCard
          label="Confidence Score"
          value={confidenceScore}
          tooltip="Reflects how consistently you answer correctly. A high confidence means stable performance; low confidence triggers more practice questions."
          color={accentColor}
        />
      </div>
    </div>
  )
}
