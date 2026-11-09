import type { Metadata, Viewport } from "next";
import "./globals.css";
import { ToastContainer } from "../components/toast";

export const metadata: Metadata = {
  title: "Narrativ Forge — Cinematic AI & Video Studio",
  description: "Burmese short-form video production & Manga AI workspace",
  icons: { icon: "/logo.svg" },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: "#080d18",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="my">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+Myanmar:wght@400;500;600;700&family=Padauk:wght@400;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        {children}
        <ToastContainer />
        {/* Telegram Web App SDK for seamless Mini App integration */}
        <script src="https://telegram.org/js/telegram-web-app.js" async />
      </body>
    </html>
  );
}
