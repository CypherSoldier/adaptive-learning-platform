"use client"

import { Navbar } from "@/components/navbar"
import { Footer } from "@/components/footer"
import { TrackProgressCard } from "@/components/track-progress-card"
import { useEffect, useState, useContext } from "react";
import axios from 'axios';
import { auth } from '@/lib/firebase';
import AuthContext from "@/app/context/AuthContext"
import { useRouter } from "next/navigation";


const colours = [
  { accentColor: "#22c55e", iconBg: "#22c55e15" },
  { accentColor: "#06b6d4", iconBg: "#06b6d415" },
  { accentColor: "#3b82f6", iconBg: "#3b82f615" }
]

interface SkillProfile {
  user_id: number;
  track_id: number,
  track_type: string,
  skill_score: number;
  confidence_score: number;
  id: number;
}

export default function ProgressPage() {
  const { user, isLoggedIn, authLoading } = useContext(AuthContext);
  const [progress, setProgress] = useState<SkillProfile[]>([]);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !isLoggedIn) {
      router.push("/login?redirect=/progress");
    }
  }, [authLoading, isLoggedIn, router]);
 
  useEffect(() => {
    if (!user?.uid) return; 
 
    axios
      .get(`${process.env.NEXT_PUBLIC_API_URL}/users/skill-profiles?user_id=${user.id}`)
      .then((response) => {
        setProgress(response.data);
      })
      .catch((error) => {
        console.error("Error fetching skill profiles:", error);
        setFetchError("Failed to load your progress. Please try again.");
      });
  }, [user?.uid]); 
 
  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Navbar />

      <main className="flex-1">
        <div className="mx-auto max-w-5xl px-6 py-12">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground">My Progress</h1>
            <p className="mt-2 text-muted-foreground">
              Track your skill development and confidence across all learning paths.
            </p>
          </div>

          <div className="grid gap-6">
            {fetchError && (
              <p className="text-sm text-destructive">{fetchError}</p>
            )}

            {progress.length > 0 ? (
              progress.map((profile, i) => (
                <TrackProgressCard
                  key={profile.id}
                  title={profile.track_type}
                  skillScore={Math.round(profile.skill_score * 100) / 100}
                  confidenceScore={Math.round(profile.confidence_score * 100) / 100}
                  accentColor={colours[i].accentColor}
                  iconBg={colours[i].iconBg}
                />
              ))
            ) : (
              !fetchError && (
                <p className="text-sm text-muted-foreground">
                  No skill profiles found yet. Complete a learning session to see your progress here.
                </p>
              )
            )}
            {/*
            <p className="mt-6 text-sm text-muted-foreground">Sample tracks (demo only):</p>
            {trackData.map((track) => (
              <TrackProgressCard
                key={track.title}
                title={track.title}
                skillScore={track.skillScore}
                confidenceScore={track.confidenceScore}
                accentColor={track.accentColor}
                iconBg={track.iconBg}
              />
            ))}
            */}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  )
}
