import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
// import { auth } from '../lib/firebase';
interface AvatarDemoProps {
  user: { photo_url?: string | null; full_name?: string | null; email?: string | null } | null | undefined
}


export function AvatarDemo({ user }: AvatarDemoProps) {
  const name = user?.full_name || user?.email || "User"
  const initials = name.split(/[\s@._-]+/).filter(Boolean).slice(0, 2).map((part) => part[0].toUpperCase()).join("") || "U"
  return (
    <Avatar>
      <AvatarImage
        src={user?.photo_url || ""}
        alt={name}
        className="grayscale"
        referrerPolicy="no-referrer"
      />
      <AvatarFallback>{initials}</AvatarFallback>
    </Avatar>
  )
}
