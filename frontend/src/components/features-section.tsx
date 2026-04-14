import { Brain, BarChart3, Target, Zap } from "lucide-react"
import { FeatureCard } from "@/components/feature-card"

const features = [
  {
    icon: Brain,
    title: "Adaptive Questions",
    description: "MCQs adjust difficulty based on your performance in real time.",
    accentColor: "#06b6d4",
  },
  {
    icon: BarChart3,
    title: "Skill Analytics",
    description: "Track your scores across topics with detailed breakdowns.",
    accentColor: "#3b82f6",
  },
  {
    icon: Target,
    title: "Focused Practice",
    description: "Weak areas are identified and targeted for improvement.",
    accentColor: "#f59e0b",
  },
  {
    icon: Zap,
    title: "Instant Feedback",
    description: "Get explanations for every answer to deepen understanding.",
    accentColor: "#22c55e",
  },
]

export function FeaturesSection() {
  return (
    <section className="border-t border-border bg-secondary px-6 py-20">
      <div className="mx-auto max-w-7xl">
        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
          Platform Features
        </p>
        <h2 className="mt-3 max-w-md text-balance text-2xl font-bold leading-snug text-foreground md:text-3xl">
          Built to help you learn smarter, not harder.
        </h2>

        <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((feature) => (
            <FeatureCard key={feature.title} {...feature} />
          ))}
        </div>
      </div>
    </section>
  )
}
