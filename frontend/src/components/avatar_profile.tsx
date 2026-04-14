import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
// import { auth } from '../lib/firebase';
import { User } from "firebase/auth"

interface AvatarDemoProps {
  user: User | null | undefined
}

// Binding element 'user' implicitly has an 'any' type.
export function AvatarDemo({ user }: AvatarDemoProps) {
  console.log('User:', user);
  console.log('User image:', user?.photoURL);

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