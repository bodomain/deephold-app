import Link from "next/link";
import {
  Database,
  LineChart,
  GitCompare,
  LayoutDashboard,
} from "lucide-react";

export function TopNav() {
  return (
    <nav className="border-b bg-card">
      <div className="container mx-auto px-4 h-14 flex items-center justify-between">
        <Link href="/" className="font-bold text-xl">
          deephold
        </Link>
        <div className="flex items-center gap-6">
          <NavLink
            href="/"
            icon={<LayoutDashboard className="h-4 w-4" />}
            label="Dashboard"
          />
          <NavLink
            href="/series"
            icon={<Database className="h-4 w-4" />}
            label="Series"
          />
          <NavLink
            href="/compare"
            icon={<GitCompare className="h-4 w-4" />}
            label="Compare"
          />
          <NavLink
            href="/correlation"
            icon={<LineChart className="h-4 w-4" />}
            label="Correlation"
          />
        </div>
      </div>
    </nav>
  );
}

function NavLink({
  href,
  icon,
  label,
}: {
  href: string;
  icon: React.ReactNode;
  label: string;
}) {
  return (
    <Link
      href={href}
      className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
    >
      {icon}
      {label}
    </Link>
  );
}
