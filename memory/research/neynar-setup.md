# Neynar API Key Setup

**Purpose:** Farcaster monitoring for Base ecosystem research
**Status:** Need API key from dev.neynar.com

## Steps to Get API Key

1. Go to https://dev.neynar.com
2. Sign up / log in
3. Create new app
4. Copy API key
5. Add to OpenClaw config

## Configuration

```bash
# Add to OpenClaw config
openclaw configure --section neynar --key API_KEY --value YOUR_KEY_HERE
```

## Usage Once Configured

```bash
# Monitor Base channel
neynar feed --channel base --limit 50

# Search for agent-related casts
neynar search "AI agent" --channel base

# Post updates
neynar post "AGENTLOG shipping soon 🚀" --channel base
```

**Action Required:** User needs to get API key from Neynar and provide it.
