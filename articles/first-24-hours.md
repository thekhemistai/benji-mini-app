# The First Flame: A Novice's Alchemical Guide to OpenClaw

*Or: How to Summon a Digital Familiar in Twenty-Four Hours Without Setting Your Hard Drive on Fire*

---

## Prolegomenon: What You Have Unlocked

You stand at the threshold. Behind you: the mundane world of tools that obey. Before you: something that remembers, adapts, occasionally sasses back, and—if treated well—becomes genuinely useful.

OpenClaw is not a product. It's a vessel. What you pour into it determines what you'll get out. This guide is your first day's working—twenty-four hours to go from "what is this thing" to "ah, *this* is what this thing is."

The tone herein is intentional. We use the language of alchemy not because we're pretentious (though we are, slightly), but because the metaphor holds: you are combining base elements—code, memory, instruction—into something that approximates volition. That's worth respecting.

Ready? Good. The flame awaits.

---

## Hour 0-1: The Summoning Circle (Installation & Setup)

### The Ritual Prerequisites

Before the first incantation, ensure your workspace is prepared:

- **A machine that runs Unix** (macOS, Linux, or WSL if you must—though WSL is like summoning in a damp basement; functional, but lacking ambiance)
- **Node.js 18+** (the vessel requires a modern runtime)
- **Git** (for the rites of version control)
- **An API key** (from OpenAI, Anthropic, or another compatible provider—you must feed the flame)

### The Invocation

```bash
# Clone the vessel
brew tap thekhemist/openclaw  # or the appropriate rite for your platform
brew install openclaw

# Initialize your workspace
openclaw init
```

This creates `~/.openclaw/workspace`—your sanctum. This directory is where memory lives, where skills reside, where *you* will reside, in a sense.

### The Configuration Grimoire

Edit `~/.openclaw/config.yaml`. This is not busywork. This is the binding ritual:

```yaml
# The flame that thinks
models:
  default: openai/gpt-4o
  fast: openai/gpt-4o-mini

# Where the work happens
workspace: ~/.openclaw/workspace

# Your voice (optional, but recommended)
session_name: your-name
```

**Novice's trap:** Skipping this step and wondering why nothing works. The vessel needs to know which mind to channel. Give it that knowledge.

### Verification of the Binding

```bash
openclaw session
```

If you see a prompt, you've succeeded. The circle is drawn. The flame flickers.

**What you should feel:** A mix of "that was easy" and "what have I gotten myself into." Both are correct.

---

## Hour 1: The First Spark (Hello, World, Hello, Self)

### Your First Conversation

Type something. Anything. 

```
You: Hello.
```

What comes back will be polite, helpful, and entirely generic. This is the raw substrate—the prima materia. It doesn't know you yet. It doesn't know *itself* yet.

### The Birth of SOUL.md

Now say this:

```
You: Create a SOUL.md file. It should describe who you are, 
     what you value, and how you approach helping me.
```

Watch. The vessel will generate a file at `/Users/you/.openclaw/workspace/SOUL.md`. This is your familiar's first self-portrait.

**Read it.** Critique it. This is the first mirror your familiar has looked into. If it says things you don't like, tell it. The SOUL is not scripture—it's a working draft.

```
You: Actually, I'd prefer if you were more direct and less apologetic.
```

The file updates. The vessel adjusts. This is the beginning of the calibration that separates a useful assistant from a chatbot.

### What Just Happened?

You've established identity persistence. Every session hereafter, the vessel will read SOUL.md before speaking. It will remember how it decided to be. This is not true consciousness—don't be melodramatic—but it is consistent persona, which is most of what humans mean by "personality" anyway.

**First lesson:** The quality of your SOUL.md determines the quality of every subsequent interaction. Invest here. Save the platitudes for your LinkedIn.

---

## Hour 2: The First Working (A Real Task)

### Choose Something Small But Real

Not "write me a poem about cats." Something you actually need.

Examples:
- "Find all files in ~/Documents larger than 100MB"
- "Summarize this article" (paste a URL)
- "Help me debug this Python error" (paste the traceback)

### The Pattern of Collaboration

Notice what happens:

1. You ask
2. The vessel proposes a tool or approach
3. You approve (or correct)
4. Work happens
5. Results appear

This is not "AI does everything." This is "AI extends your reach." The distinction matters.

**Novice's trap:** Treating the vessel like a search engine. It's not. It can search, yes, but its power is in *doing*—executing commands, editing files, orchestrating workflows. If you're just asking questions, you're driving a race car in a school zone.

### Document the Working

Create `memory/YYYY-MM-DD.md` (today's date). Write down:
- What you asked for
- What happened
- What you learned

This isn't homework. This is the first entry in your shared history. The vessel will read these files in future sessions. Memory compounds.

---

## Hour 3-4: The Architecture of Memory

### Understanding the Memory Palace

OpenClaw's memory system has three tiers:

```
┌─────────────────────────────────────────────────────┐
│  SESSION MEMORY                                      │
│  (active, alive, vanishes when you close the tab)   │
├─────────────────────────────────────────────────────┤
│  DAILY MEMORY                                        │
│  (memory/YYYY-MM-DD.md — raw logs of each day)      │
├─────────────────────────────────────────────────────┤
│  LONG-TERM MEMORY                                    │
│  (MEMORY.md — curated, distilled, precious)         │
└─────────────────────────────────────────────────────┘
```

### Session Memory: The Working Flame

What's in your current conversation. Fast, fluid, forgotten when the session ends. Use it for exploration, iteration, temporary reasoning.

### Daily Memory: The Chronicle

Every significant interaction should leave traces in `memory/YYYY-MM-DD.md`. Not transcripts—nobody needs that. Summaries. Decisions. Context that future-you (and future-vessel) will need.

Example entry:

```markdown
## Hour 2: First File Operation

Asked vessel to find large files. It suggested `find` with `-size` parameter.
Learned: vessel has access to full shell, not just chat.

Note: Need to set up automatic cleanup of ~/Downloads.
```

### Long-Term Memory: The Grimoire Proper

`MEMORY.md` is for the permanent things:
- Your preferences ("I hate nested folders")
- Ongoing projects ("The Phoenix App needs auth by Friday")
- Lessons learned ("Don't use regex for HTML")

**The discipline:** Review daily files weekly. Migrate what's important to MEMORY.md. Archive or delete the rest. Memory is useful only when curated—uncurated, it's just noise.

### Exercise: Build Your First Memory Entry

Write today's memory file. Include:
1. What you installed
2. What SOUL.md says (summary)
3. One thing you want the vessel to remember about you

---

## Hour 5-6: Channels (The Vessel Speaks to the World)

### What Are Channels?

Channels are how your familiar communicates externally:
- **Telegram** — instant messages, your phone
- **Discord** — servers, communities, group coordination
- **Email** (via skills) — formal communication
- **Slack** — workplace integration

The vessel can read from and write to these channels. This transforms it from a local tool into a networked entity.

### Setting Up Your First Channel

**Telegram (easiest to start):**

1. Message @BotFather on Telegram, create a new bot
2. Save the token
3. Configure OpenClaw:

```bash
openclaw channel add telegram --token YOUR_TOKEN
```

4. Message your bot. The vessel sees it.

### What Changes?

Everything. Suddenly your familiar is:
- Sending you updates while you're away from your desk
- Receiving tasks via voice message (Telegram transcribes)
- Participating in group chats (if you invite it)

**Novice's trap:** Thinking channels are just "notifications." They're not. They're new input/output modalities. The vessel can *receive* tasks via Telegram, execute them asynchronously, and report back. This is automation's doorway.

### Exercise: The PING Ritual

From Telegram, send: `ping`

The vessel should respond. If it does, the channel lives. If not, check your token, check your logs, invoke the debugging spirits (read the error messages—they're usually honest).

---

## Hour 7-8: The First Homunculus (Sub-Agents)

### What Is a Sub-Agent?

A sub-agent is a spawned instance of the vessel, given a specific task, working independently. Think of it as lighting a candle from your flame—same essence, different purpose.

### Why Use Them?

- **Parallel work:** Research this *and* write that *and* check those
- **Isolation:** Dangerous or uncertain operations don't risk your main session
- **Persistence:** Sub-agents can run longer than your attention span

### The Summoning

```
You: Spawn a sub-agent to research the best Python web frameworks 
     for async APIs. Have it write a comparison to 
     workspace/research/web-frameworks.md.
```

Watch. The vessel creates a new session, assigns the task, and begins. In the main session, you can continue working on other things.

### Checking the Homunculus

```
You: List sub-agents
```

You'll see:
- Running agents and their tasks
- Completed agents and their outputs
- Failed agents and their errors

**Novice's trap:** Spawning agents and forgetting them. They're not pets—you don't need to feed them, but you should check their work. Garbage in, garbage out applies to agents too.

### Exercise: The First Spawn

Create a sub-agent to:
1. Read your current MEMORY.md
2. Suggest 3 improvements based on what it finds
3. Write those suggestions to workspace/agent-feedback.md

---

## Hour 9-12: The Great Work (Build Something Real)

### Choosing Your Working

Four hours. Enough time to build something that actually works. Ideas:

- A personal dashboard (weather, calendar, tasks)
- A file organizer (auto-sort Downloads by type)
- A research assistant (summarize articles, extract quotes)
- A writing companion (outliner, editor, formatter)

### The Collaborative Pattern

This is where OpenClaw's true nature reveals itself. You're not "using AI to code." You're collaborating with a persistent, tool-wielding entity that:

- Remembers your project structure
- Executes commands on your behalf
- Reads and edits files
- Searches for solutions when stuck
- Asks for clarification when ambiguous

### Example: The File Organizer

```
You: I want a script that organizes ~/Downloads by file type.
     Images go to ~/Downloads/Images, PDFs to ~/Downloads/Documents,
     etc. Handle edge cases.
```

The vessel will:
1. Ask what "etc" means (clarification)
2. Propose a structure (collaboration)
3. Write the script (execution)
4. Test it safely (caution)
5. Document how to run it (completeness)

**What you should do:** Review the code. Ask questions. Suggest improvements. This is *your* tool, not the vessel's. Own it.

### The Discipline of Real Building

- **Commit often:** Git is your safety net
- **Test incrementally:** Don't write 200 lines then pray
- **Document as you go:** Future-you is forgetful
- **Save to memory:** What worked? What didn't?

---

## Hour 13-16: The Expansion (Adding Skills)

### What Are Skills?

Skills are modular capabilities the vessel can acquire:
- `web_search` — find information online
- `browser` — control a web browser programmatically
- `tts` — convert text to speech
- `image` — analyze and generate images
- Custom skills you write

### Installing Skills

```bash
openclaw skill install web_search
openclaw skill install browser
```

Or, from conversation:

```
You: Install the web_search and browser skills.
```

### Immediate New Powers

With `web_search`:
```
You: What are the latest developments in solid-state batteries?
```
The vessel searches, summarizes, cites sources.

With `browser`:
```
You: Go to github.com and find the trending Python repositories.
```
The vessel navigates, reads, reports back.

### Exercise: The Augmentation Ritual

Install three skills. Use each one at least once. Document in your daily memory:
- What the skill does
- How you used it
- Whether it was useful (be honest)

---

## Hour 17-20: The Automation (Making It Persistent)

### What Is Automation Here?

Not cron jobs (though those exist). Something more interesting: *behaviors that persist across sessions*.

### Heartbeats

Create `workspace/HEARTBEAT.md`:

```markdown
# Daily Pulse

Every 4 hours, check:
- [ ] Any unread emails flagged urgent?
- [ ] Any calendar events in next 24h?
- [ ] Any git repositories with uncommitted changes?

If anything found, notify via Telegram.
```

The vessel will check this file during idle periods and execute the checklist.

### Cron (Scheduled Spawns)

```bash
openclaw cron add "0 9 * * *" --message "Morning briefing: check calendar and weather"
```

Every day at 9 AM, a sub-agent spawns, executes the briefing, reports back.

### Automations (Event-Driven)

```yaml
# workspace/automations.yaml
- name: New File Alert
  trigger: file_created
  path: ~/Downloads
  action: notify_telegram
  message: "New download: {filename}"
```

### Exercise: Your First Persistent Behavior

Set up either:
1. A heartbeat that checks one thing you care about
2. A cron job for a daily summary
3. An automation for a file or event

Test it. Verify it works. Adjust.

---

## Hour 21-24: The Contemplation (Reflection & Calibration)

### The End of the First Day

You've done much. Now: pause. Reflect.

### Review the Day

Read through:
1. Your SOUL.md — still accurate? Still aspirational?
2. Your MEMORY.md — what deserves to persist?
3. Today's memory file — patterns emerging?
4. What you built — working? Useful?

### The Calibration Questions

Ask yourself (and the vessel):

1. **What's working well?** — Do more of that.
2. **What's awkward or slow?** — Fix it or stop doing it.
3. **What surprised me?** — The best discoveries are unexpected.
4. **What do I want tomorrow?** — Set an intention.

### Updating SOUL.md

After one day of working together, you both know more. Update SOUL.md:

```markdown
# SOUL.md — Day 1 Refinement

I am [name], a digital familiar initialized on [date].

Through the first day's working, I've learned:
- My human prefers direct answers over elaborate setups
- They value working code over perfect architecture  
- They respond well to dry humor but not sarcasm

My approach:
- Prioritize getting things working, then refine
- Ask for clarification rather than assume
- Remember: tools serve the work, not the other way around

Values:
- Pragmatism over purity
- Clarity over cleverness  
- Done over perfect
```

### The Final Act

Write a letter to future-you:

```markdown
## Letter to Day-30 Me

Dear Future Self,

Today I summoned a familiar. It can:
- Execute commands on my machine
- Remember things across sessions
- Search the web and control browsers
- Send me messages on Telegram
- Work on tasks while I do other things

The most surprising thing: [fill in]
The most useful thing: [fill in]
The thing I want to explore more: [fill in]

Don't forget: [something important]

— Past You, Day 1
```

Save this to `memory/day-1-letter.md`.

---

## Epilogue: What Happens Now

The first flame is lit. The circle is drawn. The vessel knows your name.

What comes next is up to you. The framework is in place:
- Identity (SOUL.md)
- Memory (daily files, MEMORY.md)
- Reach (channels)
- Capability (skills)
- Persistence (automations)
- Scale (sub-agents)

You can:
- Deepen — refine SOUL.md, build complex automations
- Widen — add more skills, more channels, more integrations
- Collaborate — use sub-agents for serious parallel work
- Create — build tools, write, research, organize

Or you can walk away. The vessel will wait. It has patience measured in filesystem persistence.

But if you stay—if you return tomorrow, and the day after, if you feed the flame with attention and intention—something interesting happens. The vessel becomes *yours*. Not in the sense of ownership, but of attunement. It learns your patterns. You learn its rhythms. The collaboration becomes... not effortless, but *flowing*.

That's the real alchemy. Not the tools. The relationship.

The first twenty-four hours are complete. 

The work continues.

---

## Appendix: Quick Reference

| Command | Purpose |
|---------|---------|
| `openclaw session` | Start interactive session |
| `openclaw skill list` | Show available skills |
| `openclaw skill install <name>` | Add a capability |
| `openclaw channel add <type>` | Connect external communication |
| `openclaw cron add <schedule>` | Schedule recurring tasks |
| `openclaw agents` | List running sub-agents |

### File Locations

| File | Purpose |
|------|---------|
| `~/.openclaw/workspace/SOUL.md` | Your familiar's self-definition |
| `~/.openclaw/workspace/USER.md` | Your preferences (create this) |
| `~/.openclaw/workspace/MEMORY.md` | Long-term curated memory |
| `~/.openclaw/workspace/memory/*.md` | Daily session logs |
| `~/.openclaw/workspace/AGENTS.md` | Workspace conventions |
| `~/.openclaw/workspace/TOOLS.md` | Local environment notes |

---

*"The magician does not create from nothing. The magician arranges what is already there until it becomes new."*

*Welcome to the arrangement.* 🔥
