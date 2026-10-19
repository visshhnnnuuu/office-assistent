import './globals.css'
import type { Metadata } from 'next'
import { Noto_Sans, Noto_Sans_Devanagari, Noto_Sans_Malayalam } from 'next/font/google'

const notoSans = Noto_Sans({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-noto-sans',
  display: 'swap',
})

const notoDeva = Noto_Sans_Devanagari({
  subsets: ['devanagari'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-noto-deva',
  display: 'swap',
})

const notoMlym = Noto_Sans_Malayalam({
  subsets: ['malayalam'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-noto-mlym',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'Office Knowledge Assistant',
  description: 'Private, grounded enterprise multilingual assistant with zero-hallucination RAG and role-based access control.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${notoSans.variable} ${notoDeva.variable} ${notoMlym.variable}`}>
      <body className="min-h-screen bg-claude-bg text-claude-text font-sans selection:bg-[#F0D5C3]">
        {children}
      </body>
    </html>
  )
}
