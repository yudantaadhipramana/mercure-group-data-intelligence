import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LensaData — Mercure Group Intelligence",
  description: "Hospitality & F&B Group Data Intelligence Demo",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
