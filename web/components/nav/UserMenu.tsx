"use client";

import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";

export function UserMenu() {
  const { user, logout, loading } = useAuth();
  const router = useRouter();

  if (loading) {
    return <div className="w-8 h-8" />;
  }

  if (!user) {
    return (
      <Button variant="outline" size="sm" onClick={() => router.push("/login")}>
        Login
      </Button>
    );
  }

  return (
    <div className="flex items-center gap-3">
      <span className="text-sm text-muted-foreground">
        {user.name || user.email}
      </span>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => {
          logout();
          router.push("/login");
        }}
      >
        Logout
      </Button>
    </div>
  );
}
