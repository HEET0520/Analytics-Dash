// frontend/app/layout.js
import "./globals.css";
import ThemeShell from "../components/shared/ThemeShell";
import Footer from "../components/shared/Footer"; // Import the new Footer component

export const metadata = {
  title: "Analytics Dash",
  description: "AI-powered financial analysis platform",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-lightbg text-neutral-900 dark:bg-darkbg dark:text-neutral-50">
        <ThemeShell>{children}</ThemeShell>
        <Footer />
      </body>
    </html>
  );
}