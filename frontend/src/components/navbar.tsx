"use client"

import Link from "next/link"
import { Brain, User, LogOut } from "lucide-react"
import { auth } from '../lib/firebase';
import { AvatarDemo } from "./avatar_profile";
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useRouter } from "next/navigation";
import AuthContext from "@/app/context/AuthContext"
import { useAuthState } from 'react-firebase-hooks/auth';
import { useContext } from "react";

export function Navbar() {
  const { user, logout, isLoggedIn } = useContext(AuthContext);
  const [g_user] = useAuthState(auth);
  const router = useRouter()

  const handleProgressClick = (e: React.MouseEvent) => {
    if (!isLoggedIn) {
      e.preventDefault()
      router.push("/login")
    }
  }

  const handleLogout = async () => {
    try {
      if (auth.currentUser) {
        await auth.signOut();
      }

      await logout();     

      router.push("/")
    } catch (error) {
      console.error("Logout error:", error);
    }
  };


  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-md">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full border border-primary/40 text-primary">
            <Brain className="h-4 w-4" />
          </div>
          <span className="text-lg font-semibold text-foreground">AdaptLearn</span>
        </Link>

        <div className="flex items-center gap-4">
          <Link
            href={isLoggedIn ? "/progress" : "/login"}
            onClick={handleProgressClick}
            className="text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            My Progress
          </Link>

          {isLoggedIn ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button
                  className="flex h-8 w-8 items-center justify-center rounded-full border border-border text-muted-foreground transition-colors hover:border-primary/40 hover:text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40"
                  aria-label="User menu"
                >
                  <User className="h-4 w-4" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col gap-1">
                    {/*<p className="text-sm font-medium">{user?.full}</p>*/}
                    <p className="text-xs text-muted-foreground">{user?.email}</p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link href="/progress" className="cursor-pointer">
                    <AvatarDemo user={g_user} />
                    {/* <User className="h-4 w-4" /> */}
                    <span className="sr-only">Profile</span>
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={handleLogout}
                  className="cursor-pointer text-destructive focus:text-destructive"
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <Button asChild variant="outline" size="sm">
              <Link href="/login">Log in</Link>
            </Button>
          )}
        </div>
      </nav>
    </header>
  )
}