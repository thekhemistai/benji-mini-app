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

const CANVAS_WIDTH = 400
const CANVAS_HEIGHT = 600
const BENJI_SIZE = 28 // Smaller for mobile maneuverability
const BOUNDARY_PADDING = 8 // Keep BENJI this far from edges

// Movement settings - FAST 1:1 tracking for high-speed gameplay
const MOVEMENT = {
  desktop: {
    followSpeed: 1.0, // Instant 1:1 mouse tracking
    smoothing: 0, // Zero smoothing - raw input
  },
  mobile: {
    followSpeed: 1.0, // Instant 1:1 touch tracking
    smoothing: 0, // Zero smoothing - react immediately
  }
}

export default function Game() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const targetPosRef = useRef({ x: CANVAS_WIDTH / 2, y: CANVAS_HEIGHT / 2 })
  const isMobileRef = useRef(false)
  
  const gameStateRef = useRef<GameState>({
    benji: { x: CANVAS_WIDTH / 2 - BENJI_SIZE / 2, y: CANVAS_HEIGHT / 2, size: BENJI_SIZE },
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
  const animationRef = useRef<number>()
  const lastTimeRef = useRef<number>(0)

  // Detect mobile on mount
  useEffect(() => {
    isMobileRef.current = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
      navigator.userAgent
    )
  }, [])

  // Initialize SDK and get user context
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
      benji: { x: CANVAS_WIDTH / 2 - BENJI_SIZE / 2, y: CANVAS_HEIGHT / 2, size: BENJI_SIZE },
      objects: [],
      score: 0,
      lives: 3,
      wave: 1,
      gameOver: false,
      started: true,
      paused: false
    }
    targetPosRef.current = { x: CANVAS_WIDTH / 2, y: CANVAS_HEIGHT / 2 }
    setDisplayState({ ...gameStateRef.current })
  }, [])

  const startGame = useCallback(() => {
    gameStateRef.current.started = true
    setDisplayState({ ...gameStateRef.current })
  }, [])

  // Full 2D movement tracking with boundary constraints
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code === 'Space') {
        e.preventDefault()
        if (!gameStateRef.current.started) {
          startGame()
        } else if (gameStateRef.current.gameOver) {
          resetGame()
        }
      }
    }

    // Convert screen coordinates to canvas coordinates with boundaries
    const constrainToBounds = (x: number, y: number) => {
      return {
        x: Math.max(BOUNDARY_PADDING, Math.min(CANVAS_WIDTH - BENJI_SIZE - BOUNDARY_PADDING, x)),
        y: Math.max(BOUNDARY_PADDING, Math.min(CANVAS_HEIGHT - BENJI_SIZE - BOUNDARY_PADDING, y))
      }
    }

    // Mouse movement - full 2D tracking
    const handleMouseMove = (e: MouseEvent) => {
      if (!gameStateRef.current.started || gameStateRef.current.gameOver) return
      
      const rect = canvas.getBoundingClientRect()
      const scaleX = CANVAS_WIDTH / rect.width
      const scaleY = CANVAS_HEIGHT / rect.height
      
      const mouseX = (e.clientX - rect.left) * scaleX - BENJI_SIZE / 2
      const mouseY = (e.clientY - rect.top) * scaleY - BENJI_SIZE / 2
      
      targetPosRef.current = constrainToBounds(mouseX, mouseY)
    }

    // Touch movement - full 2D tracking with mobile settings
    const handleTouchMove = (e: TouchEvent) => {
      if (!gameStateRef.current.started || gameStateRef.current.gameOver) return
      e.preventDefault()
      
      const rect = canvas.getBoundingClientRect()
      const scaleX = CANVAS_WIDTH / rect.width
      const scaleY = CANVAS_HEIGHT / rect.height
      
      const touch = e.touches[0]
      const touchX = (touch.clientX - rect.left) * scaleX - BENJI_SIZE / 2
      const touchY = (touch.clientY - rect.top) * scaleY - BENJI_SIZE / 2
      
      targetPosRef.current = constrainToBounds(touchX, touchY)
    }

    // Tap to start/restart
    const handleTap = (e: MouseEvent | TouchEvent) => {
      const rect = canvas.getBoundingClientRect()
      const y = 'touches' in e 
        ? e.touches[0].clientY - rect.top 
        : (e as MouseEvent).clientY - rect.top
      
      // Don't trigger if tapping share button area
      if (y > CANVAS_HEIGHT / 2 + 160 && y < CANVAS_HEIGHT / 2 + 200) {
        return
      }

      if (!gameStateRef.current.started) {
        startGame()
      } else if (gameStateRef.current.gameOver) {
        resetGame()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    canvas.addEventListener('mousemove', handleMouseMove)
    canvas.addEventListener('touchmove', handleTouchMove, { passive: false })
    canvas.addEventListener('click', handleTap)
    canvas.addEventListener('touchstart', handleTap)

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
      canvas.removeEventListener('mousemove', handleMouseMove)
      canvas.removeEventListener('touchmove', handleTouchMove)
      canvas.removeEventListener('click', handleTap)
      canvas.removeEventListener('touchstart', handleTap)
    }
  }, [startGame, resetGame])

  // Spawn objects
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
      x = BOUNDARY_PADDING + Math.random() * (CANVAS_WIDTH - size - BOUNDARY_PADDING * 2)
      y = BOUNDARY_PADDING + Math.random() * (CANVAS_HEIGHT - size - BOUNDARY_PADDING * 2)
      vx = 0
      vy = 0 // Static!
    } else {
      // Enemies: spawn from edges, move across screen
      type = Math.random() < 0.5 ? 'fud' : 'whale'
      size = type === 'whale' ? 32 : 28
      
      // SLOWER base speed, gentler progression
      const baseSpeed = 1.2 + state.wave * 0.15 // Was 2 + wave * 0.3
      
      // Pick a random edge to spawn from
      const edge = Math.floor(Math.random() * 4) // 0=top, 1=right, 2=bottom, 3=left
      
      switch (edge) {
        case 0: // Top - move down
          x = Math.random() * (CANVAS_WIDTH - size)
          y = -size
          vx = (Math.random() - 0.5) * 1.5
          vy = baseSpeed
          break
        case 1: // Right - move left
          x = CANVAS_WIDTH
          y = Math.random() * (CANVAS_HEIGHT - size)
          vx = -baseSpeed
          vy = (Math.random() - 0.5) * 1.5
          break
        case 2: // Bottom - move up
          x = Math.random() * (CANVAS_WIDTH - size)
          y = CANVAS_HEIGHT
          vx = (Math.random() - 0.5) * 1.5
          vy = -baseSpeed
          break
        case 3: // Left - move right
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

      const deltaTime = timestamp - lastTimeRef.current
      lastTimeRef.current = timestamp

      const ctx = canvasRef.current.getContext('2d')
      if (!ctx) return

      const state = gameStateRef.current
      const settings = isMobileRef.current ? MOVEMENT.mobile : MOVEMENT.desktop

      // Clear canvas
      ctx.fillStyle = '#1a1a2e'
      ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

      // Draw boundary line
      ctx.strokeStyle = '#f97316'
      ctx.lineWidth = 2
      ctx.strokeRect(
        BOUNDARY_PADDING - 2, 
        BOUNDARY_PADDING - 2, 
        CANVAS_WIDTH - (BOUNDARY_PADDING * 2) + 4, 
        CANVAS_HEIGHT - (BOUNDARY_PADDING * 2) + 4
      )

      // Draw grid background
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

      // INSTANT 1:1 tracking - no smoothing, no delay
      state.benji.x = targetPosRef.current.x
      state.benji.y = targetPosRef.current.y

      // Draw BENJI with shadow trail effect
      ctx.font = `${state.benji.size}px Arial`
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      
      // Shadow trail
      ctx.globalAlpha = 0.3
      ctx.fillText('🐕', state.benji.x + state.benji.size / 2 + 3, state.benji.y + state.benji.size / 2 + 3)
      ctx.globalAlpha = 1.0
      
      // Main BENJI
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

        // Draw object
        ctx.font = `${obj.size}px Arial`
        // Bears = enemies (fud, whale), Bones = power-ups (hype, bonus)
        const emoji = obj.type === 'fud' ? '🐻' : obj.type === 'whale' ? '🧸' : obj.type === 'hype' ? '🦴' : '🦴'
        ctx.fillText(emoji, obj.x + obj.size / 2, obj.y + obj.size / 2)

        // Check collision
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
            }
          }
          return false // Remove collected object
        }

        // Keep static power-ups, remove enemies that left screen
        if (obj.vx === 0 && obj.vy === 0) {
          return true // Power-ups stay
        }
        
        // Remove enemies that went off-screen
        return obj.x > -obj.size && obj.x < CANVAS_WIDTH + obj.size &&
               obj.y > -obj.size && obj.y < CANVAS_HEIGHT + obj.size
      })

      // Update score
      state.score += 1

      // Update wave (longer progression - 800 vs 500)
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

      // Draw lives
      ctx.textAlign = 'right'
      ctx.fillText('❤️'.repeat(state.lives), CANVAS_WIDTH - 10, 30)

      // Draw control hint
      ctx.fillStyle = 'rgba(255,255,255,0.3)'
      ctx.font = '12px Arial'
      ctx.textAlign = 'center'
      ctx.fillText(
        isMobileRef.current ? '👆 Drag to move' : '🖱️ Move mouse to control', 
        CANVAS_WIDTH / 2, 
        CANVAS_HEIGHT - 20
      )

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
  }, [displayState.started, displayState.gameOver, spawnObject, fid])

  // Draw start screen
  useEffect(() => {
    if (displayState.started) return
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    ctx.fillStyle = '#1a1a2e'
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

    // Draw boundary preview
    ctx.strokeStyle = '#f97316'
    ctx.lineWidth = 2
    ctx.strokeRect(
      BOUNDARY_PADDING - 2, 
      BOUNDARY_PADDING - 2, 
      CANVAS_WIDTH - (BOUNDARY_PADDING * 2) + 4, 
      CANVAS_HEIGHT - (BOUNDARY_PADDING * 2) + 4
    )

    ctx.fillStyle = '#f97316'
    ctx.font = 'bold 36px Arial'
    ctx.textAlign = 'center'
    ctx.fillText('🐕 BENJI', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 3)

    ctx.fillStyle = '#fff'
    ctx.font = '24px Arial'
    ctx.fillText('Survival Game', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 3 + 40)

    ctx.font = '16px Arial'
    ctx.fillStyle = '#9ca3af'
    ctx.fillText('Move freely around the screen', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 40)
    ctx.fillText('Avoid 🐻 bears from all sides!', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 70)
    ctx.fillText('Collect 🦴 bones for bonus points', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 100)

    ctx.fillStyle = '#22c55e'
    ctx.font = 'bold 20px Arial'
    ctx.fillText('TAP TO START', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 160)

    if (displayState.highScore > 0) {
      ctx.fillStyle = '#fbbf24'
      ctx.fillText(`High Score: ${displayState.highScore}`, CANVAS_WIDTH / 2, CANVAS_HEIGHT - 40)
    }
  }, [displayState.started, displayState.highScore])

  // Share challenge function
  const shareChallenge = useCallback(() => {
    if (!displayState.score) return

    const baseUrl = window.location.origin
    const challengeUrl = `${baseUrl}/challenge?score=${displayState.score}&name=${fid || 'Anonymous'}&fid=${fid || 0}`

    if (navigator.share) {
      navigator.share({
        title: 'Beat my BENJI score!',
        text: `I scored ${displayState.score} in BENJI Survival! Can you beat it?`,
        url: challengeUrl
      })
    } else {
      navigator.clipboard.writeText(challengeUrl)
    }
  }, [displayState.score, fid])

  // Draw game over screen
  useEffect(() => {
    if (!displayState.gameOver) return
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    ctx.fillStyle = 'rgba(0, 0, 0, 0.8)'
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

    ctx.fillStyle = '#f85149'
    ctx.font = 'bold 36px Arial'
    ctx.textAlign = 'center'
    ctx.fillText('GAME OVER', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 3)

    ctx.fillStyle = '#fff'
    ctx.font = '24px Arial'
    ctx.fillText(`Score: ${displayState.score}`, CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2)
    ctx.fillText(`Wave: ${displayState.wave}`, CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 35)

    if (displayState.score >= displayState.highScore && displayState.score > 0) {
      ctx.fillStyle = '#fbbf24'
      ctx.fillText('🎉 NEW HIGH SCORE! 🎉', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 80)
    }

    ctx.fillStyle = '#22c55e'
    ctx.font = 'bold 20px Arial'
    ctx.fillText('TAP TO PLAY AGAIN', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 140)

    ctx.fillStyle = '#3b82f6'
    ctx.fillText('SHARE CHALLENGE', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 180)
  }, [displayState.gameOver, displayState.score, displayState.wave, displayState.highScore])

  // Handle share click
  useEffect(() => {
    const handleShareClick = (e: MouseEvent | TouchEvent) => {
      if (!displayState.gameOver) return

      const canvas = canvasRef.current
      if (!canvas) return

      const rect = canvas.getBoundingClientRect()
      const y = ('touches' in e ? e.touches[0].clientY : e.clientY) - rect.top

      if (y > CANVAS_HEIGHT / 2 + 160 && y < CANVAS_HEIGHT / 2 + 200 && displayState.score > 0) {
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
          touchAction: 'none',
          cursor: 'none' // Hide cursor during gameplay for immersion
        }}
      />
      <p style={{ color: '#9ca3af', marginTop: '16px', fontSize: '14px' }}>
        {fid ? `Playing as FID: ${fid}` : 'Playing anonymously'}
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
