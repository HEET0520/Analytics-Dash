// frontend/app/layout.js
import "./globals.css";
import { Plus_Jakarta_Sans } from 'next/font/google';
import ThemeShell from "../components/shared/ThemeShell";
import Footer from "../components/shared/Footer"; // Import the new Footer component

export const metadata = {
  title: "Analytics Dash",
  description: "AI-powered financial analysis platform",
};

const display = Plus_Jakarta_Sans({ subsets: ['latin'], weight: ['400','500','600','700','800'], variable: '--font-display' });
const sans = Plus_Jakarta_Sans({ subsets: ['latin'], weight: ['400','500','600'], variable: '--font-sans' });

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={`min-h-screen flex flex-col bg-lightbg text-neutral-900 dark:bg-darkbg dark:text-neutral-50 ${display.variable} ${sans.variable} font-sans`}>
        <ThemeShell>{children}</ThemeShell>
        <Footer />
      </body>
    </html>
  );
}