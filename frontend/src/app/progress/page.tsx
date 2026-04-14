"use client"

import { Navbar } from "@/components/navbar"
import { Footer } from "@/components/footer"
import { TrackProgressCard } from "@/components/track-progress-card"
import { useEffect, useState, useContext, useEffectEvent } from "react";
import axios from 'axios';
import { useAuthState } from 'react-firebase-hooks/auth';
import { auth } from '@/lib/firebase';
import AuthContext from "@/app/context/AuthContext"

// Sample data
const trackData = [
  {
    title: "C++",
    skillScore: 7.2,
    confidenceScore: 8.5,
    questionsAnswered: 48,
    accentColor: "#22c55e",
    iconBg: "#22c55e15",
  },
  {
    title: "JavaScript",
    skillScore: 5.8,
    confidenceScore: 7.4,
    questionsAnswered: 35,
    accentColor: "#06b6d4",
    iconBg: "#06b6d415",
  },
]
interface User {
  user_id: number;
  email: string;
  full_name: string;
  password_hash: string;
}

interface SkillProfile {
  user_id: number;
  track_id: number,
  track_type: string,
  skill_score: number;
  confidence_score: number;
  id: number;
}

export default function ProgressPage() {
  const { jwtLoggedIn } = useContext(AuthContext);
  const [progress, setProgress] = useState<SkillProfile[]>([]);
  const [user, setUser] = useState<User>({
    user_id: 0,
    email: "",
    full_name: "",
    password_hash: ""
  });
  const [g_user] = useAuthState(auth);

  jwtLoggedIn && (
    useEffect(() => {
      axios.get('http://localhost:8000/users/me')
        .then(response => {
          setUser(response.data)
          console.log('Retrieved current user')
        })
        .catch(error => {
          console.error('Error fetching current user', error);
        })
    }, [])
  )
  
  useEffect(() => {
    // how to get logged in user_id from JWT & Google?
    // ${jwt ? user.user_id : g_user.id}
    axios.get(`http://localhost:8000/users/skill-profiles?user_id=${jwtLoggedIn ? user.user_id : g_user?.providerData[0].uid}`)
      .then(response => {
        setProgress(response.data)
        console.log('Retrieved Profile')
      })
      .catch(error => {
        console.error('There was an error fetching the profile', error);
      });
  }, []);


  console.log('Skill profile:', progress);
  //console.log(user);

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
            {progress.map((progress) => (
              <TrackProgressCard
                key={progress.id}
                title={progress.track_type}
                skillScore={Math.round(progress.skill_score * 100) / 100}
                confidenceScore={Math.round(progress.confidence_score * 100) / 100}
                accentColor={"#3b82f6"}
                iconBg={"#3b82f615"}
              />
            ))}
              <p> Sample below (C++ & JavaScript)</p>
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
          </div>
        </div>
      </main>

      <Footer />
    </div>
  )
}
