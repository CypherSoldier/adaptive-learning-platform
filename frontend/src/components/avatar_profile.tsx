import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
// import { auth } from '../lib/firebase';
import { User } from "firebase/auth"

interface AvatarDemoProps {
  user: User | null | undefined
}


export function AvatarDemo({ user }: AvatarDemoProps) {
  return (
    <Avatar>
      <AvatarImage
        src={user?.photoURL || ""}
        alt="user"
        className="grayscale"
        referrerPolicy="no-referrer"
      />
      <AvatarFallback>CN</AvatarFallback>
    </Avatar>
  )
}