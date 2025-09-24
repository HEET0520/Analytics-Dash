import "./globals.css";
import ThemeShell from "../components/shared/ThemeShell";

export const metadata = {
  title: "Analytics Dash",
  description: "AI-powered financial analysis platform",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-lightbg text-neutral-900 dark:bg-darkbg dark:text-neutral-50">
        <ThemeShell>{children}</ThemeShell>
      </body>
    </html>
  );
}
