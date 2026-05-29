// components/ui/spinner.tsx

import { Loader2 } from "lucide-react";

export function Spinner({ className }: { className?: string }) {
  return (
    <div className={className ?? "min-h-screen flex items-center justify-center"}>
      <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
    </div>
  );
}