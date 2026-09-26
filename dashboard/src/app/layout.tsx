"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode, useState } from "react";

const nav = [
  { href: "/", label: "Executive" },
  { href: "/property/", label: "Property" },
  { href: "/hotel/", label: "Hotel" },
  { href: "/fnb/", label: "F&B" },
  { href: "/finance/", label: "Finance" },
  { href: "/inventory/", label: "Inventory" },
  { href: "/quality/", label: "Quality" },
  { href: "/forecast/", label: "Forecast" },
];

export default function RootLayout({ children }: { children: ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);
  const path = usePathname();
  return (
    <html lang="en">
      <body className="antialiased bg-[#0b1121] text-slate-100">
        <div className="flex min-h-screen">
          <aside className={`${collapsed ? "w-16" : "w-64"} transition-all glass flex flex-col`}>
            <div className="p-6 border-b border-white/10">
              <div className="text-amber-100 font-light text-xl tracking-wider">LensaData</div>
              {!collapsed && <div className="text-xs text-slate-400 mt-1">Mercure Group Intelligence</div>}
            </div>
            <nav className="flex-1 p-3 space-y-1">
              {nav.map((n) => (
                <Link
                  key={n.href}
                  href={n.href}
                  className={`block px-4 py-3 rounded-lg text-sm ${path === n.href ? "bg-amber-500/20 text-amber-100" : "text-slate-300 hover:bg-white/5"}`}
                >
                  {n.label}
                </Link>
              ))}
            </nav>
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="p-3 text-xs text-slate-400 hover:text-slate-200 border-t border-white/10"
            >
              {collapsed ? ">" : "< Collapse"}
            </button>
          </aside>
          <main className="flex-1 p-6 overflow-auto">{children}</main>
        </div>
      </body>
    </html>
  );
}
