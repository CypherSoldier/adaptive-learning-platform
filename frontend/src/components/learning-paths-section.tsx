import { LearningPathCard } from "@/components/learning-path-card"

const paths = [
  {
    title: "Python",
    slug: "python",
    description:
      "Master Python from fundamentals to advanced concepts. Covers data structures, OOP, and real-world problem solving.",
    level: "Beginner \u2192 Advanced",
    modules: 12,
    progress: 0,
    accentColor: "#22c55e",
    iconBg: "#22c55e18",
    progressColor: "#22c55e",
  },
  {
    title: "C++",
    slug: "cpp",
    description:
      "Deep dive into C++ with pointers, memory management, STL, and competitive programming patterns.",
    level: "Intermediate",
    modules: 10,
    progress: 0,
    accentColor: "#3b82f6",
    iconBg: "#3b82f618",
    progressColor: "#3b82f6",
  },
  {
    title: "JavaScript",
    slug: "javascript",
    description:
      "From ES6+ fundamentals to async patterns, closures, and DOM manipulation for modern web development.",
    level: "Beginner \u2192 Intermediate",
    modules: 14,
    progress: 0,
    accentColor: "#06b6d4",
    iconBg: "#06b6d418",
    progressColor: "#06b6d4",
  },
]

export function LearningPathsSection() {
  return (
    <section className="px-6 pb-20">
      <div className="mx-auto max-w-7xl">
        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
          Learning Paths
        </p>

        <div className="mt-6 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {paths.map((path) => (
            <LearningPathCard key={path.slug} {...path} />
          ))}
        </div>
      </div>
    </section>
  )
}
