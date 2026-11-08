import type { Metadata } from "next";
import "./globals.css";
import { ToastContainer } from "../components/toast";

export const metadata: Metadata = {
  title: "Narrativ Forge — Cinematic AI & Video Studio",
  description: "Burmese short-form video production & Manga AI workspace",
  icons: { icon: "/logo.svg" },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="my">
      <body>
        {children}
        <ToastContainer />
        {/* Telegram Web App SDK for seamless Mini App integration */}
        <script src="https://telegram.org/js/telegram-web-app.js" async />
      </body>
    </html>
  );
}
