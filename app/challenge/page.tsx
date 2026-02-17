'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { sdk } from '@farcaster/miniapp-sdk'

interface GameObject {
  x: number
  y: number
  vx: number
  vy: number
  type: 'fud' | 'hype' | 'whale' | 'bonus'
  size: number
}

interface GameState {
  benji: { x: number; y: number; size: number }
  objects: GameObject[]
  score: number
  highScore: number
  lives: number
  wave: number
  gameOver: boolean
  started: boolean
  paused: boolean
}

interface Challenge {
  targetScore: number
  challengerName: string
  challengerFid: number
}

const CANVAS_WIDTH = 400
const CANVAS_HEIGHT = 600
const BENJI_SIZE = 28 // Smaller for mobile maneuverability
const GRAVITY = 0.5
const JUMP_FORCE = -12

export default function ChallengeGame() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const gameStateRef = useRef<GameState>({
    benji: { x: CANVAS_WIDTH / 2 - BENJI_SIZE / 2, y: CANVAS_HEIGHT - 100, size: BENJI_SIZE },
    objects: [],
    score: 0,
    highScore: 0,
    lives: 3,
    wave: 1,
    gameOver: false,
    started: false,
    paused: false
  })
  const [displayState, setDisplayState] = useState(gameStateRef.current)
  const [fid, setFid] = useState<number | null>(null)
  const [challenge, setChallenge] = useState<Challenge | null>(null)
  const [challengeBeaten, setChallengeBeaten] = useState(false)
  const animationRef = useRef<number>()
  const lastTimeRef = useRef<number>(0)

  // Parse challenge from URL
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const score = params.get('score')
    const name = params.get('name')
    const challengerFid = params.get('fid')

    if (score && name) {
      setChallenge({
        targetScore: parseInt(score),
        challengerName: decodeURIComponent(name),
        challengerFid: challengerFid ? parseInt(challengerFid) : 0
      })
    }
  }, [])

  // Initialize SDK
  useEffect(() => {
    const init = async () => {
      try {
        await sdk.actions.ready()
        const context = await sdk.context
        if (context?.user?.fid) {
          setFid(context.user.fid)
          const saved = localStorage.getItem(`benji-highscore-${context.user.fid}`)
          if (saved) {
            gameStateRef.current.highScore = parseInt(saved)
            setDisplayState({ ...gameStateRef.current })
          }
        }
      } catch (e) {
        console.log('SDK init:', e)
        const saved = localStorage.getItem('benji-highscore')
        if (saved) {
          gameStateRef.current.highScore = parseInt(saved)
          setDisplayState({ ...gameStateRef.current })
        }
      }
    }
    init()
  }, [])

  const resetGame = useCallback(() => {
    gameStateRef.current = {
      ...gameStateRef.current,
      benji: { x: CANVAS_WIDTH / 2 - BENJI_SIZE / 2, y: CANVAS_HEIGHT - 100, size: BENJI_SIZE },
      objects: [],
      score: 0,
      lives: 3,
      wave: 1,
      gameOver: false,
      started: true,
      paused: false
    }
    setChallengeBeaten(false)
    setDisplayState({ ...gameStateRef.current })
  }, [])

  const startGame = useCallback(() => {
    gameStateRef.current.started = true
    setDisplayState({ ...gameStateRef.current })
  }, [])

  const jump = useCallback(() => {
    if (gameStateRef.current.started && !gameStateRef.current.gameOver) {
      gameStateRef.current.benji.y = Math.max(0, gameStateRef.current.benji.y - 80)
    }
  }, [])

  // Handle input
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code === 'Space' || e.code === 'ArrowUp') {
        e.preventDefault()
        if (!gameStateRef.current.started) {
          startGame()
        } else if (gameStateRef.current.gameOver) {
          resetGame()
        } else {
          jump()
        }
      }
    }

    const handleClick = () => {
      if (!gameStateRef.current.started) {
        startGame()
      } else if (gameStateRef.current.gameOver) {
        resetGame()
      } else {
        jump()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    window.addEventListener('click', handleClick)
    window.addEventListener('touchstart', handleClick)

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
      window.removeEventListener('click', handleClick)
      window.removeEventListener('touchstart', handleClick)
    }
  }, [startGame, resetGame, jump])

  const spawnObject = useCallback((forceType?: 'enemy' | 'powerup') => {
    const state = gameStateRef.current
    
    // Decide enemy vs powerup (10% chance for powerup)
    const isPowerup = forceType === 'powerup' || (forceType === undefined && Math.random() < 0.1)
    
    let type: GameObject['type']
    let size: number
    let x: number, y: number, vx: number, vy: number
    
    if (isPowerup) {
      // Power-ups: static, spawn in play area
      type = Math.random() < 0.3 ? 'bonus' : 'hype'
      size = type === 'bonus' ? 24 : 20
      x = 20 + Math.random() * (CANVAS_WIDTH - size - 40)
      y = 20 + Math.random() * (CANVAS_HEIGHT - size - 40)
      vx = 0
      vy = 0 // Static!
    } else {
      // Enemies: spawn from edges, move across screen
      type = Math.random() < 0.5 ? 'fud' : 'whale'
      size = type === 'whale' ? 32 : 28
      
      // SLOWER base speed, gentler progression
      const baseSpeed = 1.2 + state.wave * 0.15
      
      // Pick a random edge to spawn from
      const edge = Math.floor(Math.random() * 4)
      
      switch (edge) {
        case 0: // Top
          x = Math.random() * (CANVAS_WIDTH - size)
          y = -size
          vx = (Math.random() - 0.5) * 1.5
          vy = baseSpeed
          break
        case 1: // Right
          x = CANVAS_WIDTH
          y = Math.random() * (CANVAS_HEIGHT - size)
          vx = -baseSpeed
          vy = (Math.random() - 0.5) * 1.5
          break
        case 2: // Bottom
          x = Math.random() * (CANVAS_WIDTH - size)
          y = CANVAS_HEIGHT
          vx = (Math.random() - 0.5) * 1.5
          vy = -baseSpeed
          break
        case 3: // Left
          x = -size
          y = Math.random() * (CANVAS_HEIGHT - size)
          vx = baseSpeed
          vy = (Math.random() - 0.5) * 1.5
          break
        default:
          x = Math.random() * (CANVAS_WIDTH - size)
          y = -size
          vx = (Math.random() - 0.5) * 1.5
          vy = baseSpeed
      }
    }

    const obj: GameObject = { x, y, vx, vy, type, size }
    state.objects.push(obj)
  }, [])

  // Game loop
  useEffect(() => {
    if (!displayState.started || displayState.gameOver) return

    const gameLoop = (timestamp: number) => {
      if (!canvasRef.current) return

      lastTimeRef.current = timestamp
      const ctx = canvasRef.current.getContext('2d')
      if (!ctx) return

      const state = gameStateRef.current

      // Clear and draw background
      ctx.fillStyle = '#1a1a2e'
      ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

      ctx.strokeStyle = '#2a2a4e'
      ctx.lineWidth = 1
      for (let i = 0; i < CANVAS_WIDTH; i += 40) {
        ctx.beginPath()
        ctx.moveTo(i, 0)
        ctx.lineTo(i, CANVAS_HEIGHT)
        ctx.stroke()
      }
      for (let i = 0; i < CANVAS_HEIGHT; i += 40) {
        ctx.beginPath()
        ctx.moveTo(0, i)
        ctx.lineTo(CANVAS_WIDTH, i)
        ctx.stroke()
      }

      // Challenge target line
      if (challenge && state.score < challenge.targetScore) {
        const progress = state.score / challenge.targetScore
        const barWidth = CANVAS_WIDTH - 40
        ctx.fillStyle = '#374151'
        ctx.fillRect(20, CANVAS_HEIGHT - 30, barWidth, 20)
        ctx.fillStyle = '#f97316'
        ctx.fillRect(20, CANVAS_HEIGHT - 30, barWidth * progress, 20)
        ctx.fillStyle = '#fff'
        ctx.font = 'bold 12px Arial'
        ctx.textAlign = 'center'
        ctx.fillText(`${challenge.challengerName}'s score: ${challenge.targetScore}`, CANVAS_WIDTH / 2, CANVAS_HEIGHT - 15)
      }

      // Update BENJI
      state.benji.y = Math.min(CANVAS_HEIGHT - state.benji.size - (challenge ? 40 : 0), state.benji.y + GRAVITY * 2)

      ctx.font = `${state.benji.size}px Arial`
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText('🐕', state.benji.x + state.benji.size / 2, state.benji.y + state.benji.size / 2)

      // Spawn enemies (slower rate, gentler progression)
      if (Math.random() < 0.012 + state.wave * 0.003) {
        spawnObject('enemy')
      }
      
      // Spawn power-ups rarely
      if (Math.random() < 0.002) {
        spawnObject('powerup')
      }

      // Update and draw objects
      state.objects = state.objects.filter(obj => {
        // Only move enemies (power-ups are static)
        if (obj.vx !== 0 || obj.vy !== 0) {
          obj.x += obj.vx
          obj.y += obj.vy
        }

        ctx.font = `${obj.size}px Arial`
        // Bears = enemies (fud, whale), Bones = power-ups (hype, bonus)
        const emoji = obj.type === 'fud' ? '🐻' : obj.type === 'whale' ? '🧸' : obj.type === 'hype' ? '🦴' : '🦴'
        ctx.fillText(emoji, obj.x + obj.size / 2, obj.y + obj.size / 2)

        // Collision detection
        const benji = state.benji
        const collision = 
          obj.x < benji.x + benji.size &&
          obj.x + obj.size > benji.x &&
          obj.y < benji.y + benji.size &&
          obj.y + obj.size > benji.y

        if (collision) {
          if (obj.type === 'bonus') {
            state.score += 50
          } else if (obj.type === 'hype') {
            state.score += 20
          } else {
            state.lives -= 1
            if (state.lives <= 0) {
              state.gameOver = true
              if (state.score > state.highScore) {
                state.highScore = state.score
                localStorage.setItem(`benji-highscore-${fid || 'anon'}`, state.score.toString())
              }
              // Check if challenge beaten
              if (challenge && state.score > challenge.targetScore) {
                setChallengeBeaten(true)
              }
            }
          }
          return false
        }

        // Keep static power-ups, remove enemies that left screen
        if (obj.vx === 0 && obj.vy === 0) {
          return true
        }
        
        return obj.x > -obj.size && obj.x < CANVAS_WIDTH + obj.size &&
               obj.y > -obj.size && obj.y < CANVAS_HEIGHT + obj.size
      })

      state.score += 1

      // Check challenge progress
      if (challenge && state.score > challenge.targetScore && !challengeBeaten) {
        setChallengeBeaten(true)
      }

      // Longer wave progression
      if (state.score > state.wave * 800) {
        state.wave += 1
      }

      // Draw UI
      ctx.fillStyle = '#fff'
      ctx.font = 'bold 20px Arial'
      ctx.textAlign = 'left'
      ctx.fillText(`Score: ${state.score}`, 10, 30)
      ctx.fillText(`Wave: ${state.wave}`, 10, 55)
      ctx.fillText(`Best: ${state.highScore}`, 10, 80)

      ctx.textAlign = 'right'
      ctx.fillText('❤️'.repeat(state.lives), CANVAS_WIDTH - 10, 30)

      setDisplayState({ ...state })

      if (!state.gameOver) {
        animationRef.current = requestAnimationFrame(gameLoop)
      }
    }

    animationRef.current = requestAnimationFrame(gameLoop)

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [displayState.started, displayState.gameOver, spawnObject, fid, challenge, challengeBeaten])

  // Start screen
  useEffect(() => {
    if (displayState.started) return
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    ctx.fillStyle = '#1a1a2e'
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

    ctx.fillStyle = '#f97316'
    ctx.font = 'bold 36px Arial'
    ctx.textAlign = 'center'
    ctx.fillText('🐕 BENJI', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 4)

    ctx.fillStyle = '#fff'
    ctx.font = '24px Arial'
    ctx.fillText('Survival Game', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 4 + 40)

    if (challenge) {
      ctx.fillStyle = '#fbbf24'
      ctx.font = 'bold 20px Arial'
      ctx.fillText('⚔️ CHALLENGE ⚔️', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 3 + 20)
      ctx.fillStyle = '#fff'
      ctx.font = '18px Arial'
      ctx.fillText(`Beat ${challenge.challengerName}'s`, CANVAS_WIDTH / 2, CANVAS_HEIGHT / 3 + 50)
      ctx.fillText(`score of ${challenge.targetScore}!`, CANVAS_WIDTH / 2, CANVAS_HEIGHT / 3 + 75)
    }

    ctx.font = '16px Arial'
    ctx.fillStyle = '#9ca3af'
    ctx.fillText('Tap or press SPACE to jump', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 40)
    ctx.fillText('Avoid 📉 FUD and 🐋 whales!', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 70)
    ctx.fillText('Collect 💎 for bonus points', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 100)

    ctx.fillStyle = '#22c55e'
    ctx.font = 'bold 20px Arial'
    ctx.fillText('TAP TO START', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 160)

    if (displayState.highScore > 0) {
      ctx.fillStyle = '#fbbf24'
      ctx.fillText(`Your Best: ${displayState.highScore}`, CANVAS_WIDTH / 2, CANVAS_HEIGHT - 40)
    }
  }, [displayState.started, displayState.highScore, challenge])

  // Game over screen
  useEffect(() => {
    if (!displayState.gameOver) return
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    ctx.fillStyle = 'rgba(0, 0, 0, 0.8)'
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

    ctx.fillStyle = challengeBeaten ? '#22c55e' : '#f85149'
    ctx.font = 'bold 36px Arial'
    ctx.textAlign = 'center'
    ctx.fillText(challengeBeaten ? 'CHALLENGE BEATEN!' : 'GAME OVER', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 4)

    ctx.fillStyle = '#fff'
    ctx.font = '24px Arial'
    ctx.fillText(`Score: ${displayState.score}`, CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 - 40)
    ctx.fillText(`Wave: ${displayState.wave}`, CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2)

    if (challenge && challengeBeaten) {
      ctx.fillStyle = '#fbbf24'
      ctx.font = 'bold 18px Arial'
      ctx.fillText(`You beat ${challenge.challengerName}!`, CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 40)
      ctx.fillText(`(+${displayState.score - challenge.targetScore} points)`, CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 65)
    } else if (challenge && !challengeBeaten) {
      ctx.fillStyle = '#f87171'
      ctx.font = '18px Arial'
      ctx.fillText(`${challenge.challengerName} beat you by`, CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 40)
      ctx.fillText(`${challenge.targetScore - displayState.score} points`, CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 65)
    }

    if (displayState.score >= displayState.highScore && displayState.score > 0) {
      ctx.fillStyle = '#fbbf24'
      ctx.font = 'bold 18px Arial'
      ctx.fillText('🎉 NEW HIGH SCORE! 🎉', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 110)
    }

    ctx.fillStyle = '#22c55e'
    ctx.font = 'bold 20px Arial'
    ctx.fillText('TAP TO PLAY AGAIN', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 160)

    // Share challenge button
    if (displayState.score > 0) {
      ctx.fillStyle = '#3b82f6'
      ctx.fillText('SHARE CHALLENGE', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 200)
    }
  }, [displayState.gameOver, displayState.score, displayState.wave, displayState.highScore, challenge, challengeBeaten])

  // Handle share challenge click
  const shareChallenge = useCallback(() => {
    if (!displayState.score) return
    
    const baseUrl = window.location.origin
    const challengeUrl = `${baseUrl}/challenge?score=${displayState.score}&name=${fid || 'Anonymous'}&fid=${fid || 0}`
    
    // Copy to clipboard
    navigator.clipboard.writeText(challengeUrl)
    
    // Or use Web Share API if available
    if (navigator.share) {
      navigator.share({
        title: 'Beat my BENJI score!',
        text: `I scored ${displayState.score} in BENJI Survival! Can you beat it?`,
        url: challengeUrl
      })
    }
  }, [displayState.score, fid])

  // Add click handler for share button
  useEffect(() => {
    const handleShareClick = (e: MouseEvent | TouchEvent) => {
      if (!displayState.gameOver) return
      
      const canvas = canvasRef.current
      if (!canvas) return
      
      const rect = canvas.getBoundingClientRect()
      const x = ('touches' in e ? e.touches[0].clientX : e.clientX) - rect.left
      const y = ('touches' in e ? e.touches[0].clientY : e.clientY) - rect.top
      
      // Share button area (approximate)
      if (y > CANVAS_HEIGHT / 2 + 180 && y < CANVAS_HEIGHT / 2 + 220 && displayState.score > 0) {
        e.stopPropagation()
        shareChallenge()
      }
    }

    window.addEventListener('click', handleShareClick)
    window.addEventListener('touchstart', handleShareClick)

    return () => {
      window.removeEventListener('click', handleShareClick)
      window.removeEventListener('touchstart', handleShareClick)
    }
  }, [displayState.gameOver, displayState.score, shareChallenge])

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      background: '#1a1a2e',
      padding: '20px'
    }}>
      <canvas
        ref={canvasRef}
        width={CANVAS_WIDTH}
        height={CANVAS_HEIGHT}
        style={{
          border: '2px solid #f97316',
          borderRadius: '12px',
          maxWidth: '100%',
          touchAction: 'none'
        }}
      />
      <p style={{ color: '#9ca3af', marginTop: '16px', fontSize: '14px' }}>
        {challenge ? `⚔️ Challenge from ${challenge.challengerName}` : fid ? `Playing as FID: ${fid}` : 'Playing anonymously'}
      </p>
      {displayState.gameOver && displayState.score > 0 && (
        <button
          onClick={shareChallenge}
          style={{
            marginTop: '12px',
            padding: '12px 24px',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: 'bold',
            cursor: 'pointer'
          }}
        >
          Share Challenge Link
        </button>
      )}
    </div>
  )
}
