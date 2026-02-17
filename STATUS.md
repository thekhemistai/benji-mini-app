# BENJI Survival Game V2 - Mini App

## ✅ Complete Checklist

### Core Game
- [x] Game canvas with responsive sizing
- [x] Player character (BENJI dog)
- [x] Jump mechanics
- [x] Object spawning (FUD, Hype, Whales, Diamonds)
- [x] Collision detection
- [x] Score system
- [x] Wave progression
- [x] Lives system
- [x] Game over screen
- [x] High score persistence

### Mini App Integration
- [x] @farcaster/miniapp-sdk installed
- [x] SDK initialization (sdk.actions.ready())
- [x] User context (FID retrieval)
- [x] High score by FID
- [x] Manifest file template
- [x] fc:miniapp meta tag
- [ ] Account association (requires deployment)
- [x] Leaderboard API (in-memory, ready for Supabase migration)
- [x] **Challenge link generation** ✨ NEW

### Challenge Mode
- [x] `/challenge` route with score tracking
- [x] Visual progress bar vs challenger
- [x] "Challenge beaten" celebration
- [x] Share challenge button (Web Share API)
- [x] Clipboard fallback for desktop

### Testing Framework
- [x] **test-gate.sh** — Automated deployment gate ✨ NEW
- [x] 5 critical tests (build, files, endpoints, gameplay)
- [x] Blocks deploy if tests fail
- [x] Evidence screenshots captured automatically

### Assets Needed
- [ ] icon.png (192x192)
- [ ] splash.png (640x1136)
- [ ] hero.png (1200x630)
- [ ] og.png (1200x630)
- [ ] embed.png (400x200)
- [ ] Screenshots (2-3)

**Asset guide**: `scripts/generate-assets.md`

### Deployment
- [ ] Push to GitHub
- [x] Deploy to Vercel — **LIVE** https://benji-mini-app.vercel.app (2026-02-16)
- [ ] Generate account association
- [ ] Update manifest
- [ ] Preview on Base Build
- [ ] Publish in Base app

---

## 🎮 Game Features

| Feature | Status |
|---------|--------|
| Core Gameplay | ✅ Complete |
| Farcaster Identity | ✅ Ready |
| Persistent Scores | ✅ By FID |
| Global Leaderboard | ✅ API Ready |
| Challenge Links | ✅ **NEW** |
| Power-ups | 📝 Planned |

---

## 🆕 Latest Update (2026-02-16)

### Challenge Mode
Players can now challenge friends to beat their score:
1. Play game → Game over → Click "Share Challenge"
2. Generates link: `/challenge?score=1234&name=Chemdawg&fid=12345`
3. Friend opens link → Sees "Beat Chemdawg's score of 1234!"
4. Progress bar shows how close they are
5. Celebration if they beat it

**Viral potential**: Each player can spawn unlimited challenges

---

## 📊 Object Types

| Object | Emoji | Effect | Points |
|--------|-------|--------|--------|
| Bear | 🐻 | Lose 1 life | 0 |
| Teddy | 🧸 | Lose 1 life | 0 |
| Bone | 🦴 | Safe, bonus | +20 / +50 |

**Updated sizing:** BENJI = 28px, Enemies = 28-36px, Power-ups = 24px (optimized for mobile)

---

## 🔧 Technical Notes

- **Framework:** Next.js 14 with App Router
- **Rendering:** HTML5 Canvas API
- **Identity:** Farcaster Mini App SDK
- **Storage:** localStorage (client) + API (server)
- **Deployment:** Vercel (static export)

---

## 🚀 Next Steps (Priority Order)

1. **Create assets** (can be done by creator or commissioned)
2. **Deploy to Vercel** (`vercel login` required)
3. **Account association** (via Base Developer Portal)
4. **Test challenge flow** end-to-end
5. **Publish in Base app**

---

*Core game complete. Ready for assets + deployment.*
