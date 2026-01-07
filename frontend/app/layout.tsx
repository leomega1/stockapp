import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'S&P 500 Stock Tracker',
  description: 'Track daily S&P 500 winners and losers with AI-generated insights',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <nav className="bg-gray-900 text-white shadow-lg">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex items-center justify-between h-16">
                <div className="flex items-center">
                  <h1 className="text-xl font-bold">📈 S&P 500 Tracker</h1>
                </div>
                <div className="flex space-x-4">
                  <a href="/" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700">
                    Dashboard
                  </a>
                </div>
              </div>
            </div>
          </nav>
          <main className="min-h-screen">
            {children}
          </main>
          <footer className="bg-gray-900 text-white py-6 mt-12">
            <div className="max-w-7xl mx-auto px-4 text-center">
              <p className="text-sm">© 2026 S&P 500 Stock Tracker. Powered by AI.</p>
            </div>
          </footer>
        </Providers>
      </body>
    </html>
  )
}

