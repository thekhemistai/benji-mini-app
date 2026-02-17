import { NextRequest, NextResponse } from 'next/server'

// In-memory leaderboard (replace with Supabase for production)
let leaderboard: { fid: number; username: string; score: number; wave: number; timestamp: number }[] = []

export async function GET() {
  // Return top 100 scores
  const sorted = [...leaderboard].sort((a, b) => b.score - a.score).slice(0, 100)
  return NextResponse.json({ leaderboard: sorted })
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { fid, username, score, wave } = body

    if (!fid || score === undefined) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 })
    }

    // Check if user already has a score
    const existingIndex = leaderboard.findIndex(e => e.fid === fid)
    
    if (existingIndex >= 0) {
      // Only update if new score is higher
      if (score > leaderboard[existingIndex].score) {
        leaderboard[existingIndex] = {
          fid,
          username: username || `FID:${fid}`,
          score,
          wave,
          timestamp: Date.now()
        }
      }
    } else {
      // Add new entry
      leaderboard.push({
        fid,
        username: username || `FID:${fid}`,
        score,
        wave,
        timestamp: Date.now()
      })
    }

    // Keep only top 1000 to prevent memory issues
    if (leaderboard.length > 1000) {
      leaderboard = leaderboard
        .sort((a, b) => b.score - a.score)
        .slice(0, 1000)
    }

    // Return user's rank
    const sorted = [...leaderboard].sort((a, b) => b.score - a.score)
    const rank = sorted.findIndex(e => e.fid === fid) + 1

    return NextResponse.json({ success: true, rank })
  } catch (error) {
    return NextResponse.json({ error: 'Server error' }, { status: 500 })
  }
}
