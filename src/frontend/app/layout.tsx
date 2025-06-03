import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google"
import Navigation from "@/components/Navigation"
import "./globals.css"

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
})

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
})

export const metadata: Metadata = {
  title: "Dublin Rent Predictor",
  description: "AI-powered rental price predictions for Dublin properties",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <div className="min-h-screen bg-gradient-to-br from-blue-100 to-gray-50">
          {/* Header */}
          <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
            <div className="max-w-6xl mx-auto px-4 py-4">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
                <div className="text-center md:text-left space-y-2">
                  <h1 className="text-3xl font-bold text-gray-900">Dublin Rent Predictor</h1>
                  <div className="flex items-center justify-center md:justify-start gap-4">
                    <p className="text-gray-600 w-[100vw] md:w-auto">Get an estimated rental price for properties in Dublin</p>
                  </div>
                </div>
                
                {/* Navigation */}
                <div className="flex justify-center md:justify-end">
                  <Navigation />
                </div>
              </div>
            </div>
          </header>

          {/* Main Content */}
          <main className="p-4">
            <div className="max-w-4xl mx-auto">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  )
}
