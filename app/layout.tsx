import type { Metadata } from 'next'
import { GeistSans } from 'geist/font/sans'
import { GeistMono } from 'geist/font/mono'
import './globals.css'
import MainNavigation from '@/components/MainNavigation'
import { Toaster } from '@/components/ui/toaster'

export const metadata: Metadata = {
  title: '🚀 Enhanced Vehicle Appraisal System v7.0',
  description: 'Professional vehicle trade-in management with mobile optimization, smart OCR, and advanced analytics - NUCLEAR DEPLOYMENT ACTIVE',
  generator: 'Enhanced System v7.0 - FORCE DEPLOYED',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className={`${GeistSans.variable} ${GeistMono.variable}`}>

        <style>{`
html {
  font-family: ${GeistSans.style.fontFamily};
  --font-sans: ${GeistSans.variable};
  --font-mono: ${GeistMono.variable};
}
        `}</style>
      </head>
      <body className={GeistSans.className}>
        <MainNavigation />
        <main>{children}</main>
        <Toaster />
      </body>
    </html>
  )
}
