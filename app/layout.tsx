import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'BENJI Survival Game',
  description: 'Help BENJI survive waves of FUD in this action game',
  icons: {
    icon: '/icon.png',
  },
  openGraph: {
    title: 'BENJI Survival Game',
    description: 'Survive the FUD!',
    images: ['/og.png'],
  },
  other: {
    'fc:miniapp': JSON.stringify({
      version: 'next',
      imageUrl: 'https://benji-game.vercel.app/embed.png',
      button: {
        title: 'Play Now',
        action: {
          type: 'launch_miniapp',
          name: 'BENJI Survival',
          url: 'https://benji-game.vercel.app'
        }
      }
    })
  }
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body style={{ margin: 0, padding: 0, background: '#1a1a2e' }}>
        {children}
      </body>
    </html>
  )
}
