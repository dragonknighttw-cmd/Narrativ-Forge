import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Narrativ Forge",
  description: "Burmese short-form video production workspace",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="my">
      <body>{children}</body>
    </html>
  );
}