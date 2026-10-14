import type { Metadata } from "next";
import "./globals.css";
import { ToastContainer } from "../components/toast";

export const metadata: Metadata = {
  title: "Narrativ Forge",
  description: "Burmese short-form video production workspace",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="my">
      <body>
        {children}
        <ToastContainer />
      </body>
    </html>
  );
}