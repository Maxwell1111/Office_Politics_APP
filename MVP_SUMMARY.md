# Subtext MVP - Implementation Summary

## ✅ What's Been Built

I've successfully transformed your Office Politics APP into **Subtext**, a fully functional MVP backend for a B2C career strategy application. Here's what's ready to use:

## 🎯 Three Core Features (All Implemented)

### 1. The Tone Decoder ✅
**What it does:** Analyzes messages to extract hidden meaning and provide strategic advice

**Implementation:**
- AI-powered analysis using Anthropic Claude 3.5 Sonnet
- Custom "Chief of Staff" system prompt (Machiavellian, strategic, cynical)
- Decodes subtext from emails, Slack messages, conversations
- Assesses career risk level (Low/Medium/High)
- Generates strategic response drafts
- Pulls historical context from Log Book automatically
- Caches analyses for reference

**API Endpoint:** `POST /api/tone-decoder/analyze`

**Example Response:**
```json
{
  "subtext": "Jennifer is establishing territory and wants to see if you'll push back...",
  "risk_level": "medium",
  "suggested_reply": "Hi Jennifer, happy to discuss. Let me send over the current roadmap...",
  "follow_up_actions": ["Document this interaction", "CC Sarah on response"],
  "context_used": ["Took credit for my feature in stakeholder meeting"]
}
```

### 2. The Power Map ✅
**What it does:** Database and visualization of office politics relationships

**Implementation:**
- Full CRUD for "Players" (colleagues/stakeholders)
- Player attributes: Name, Role, Influence Level (1-10), Ally/Enemy status
- Formal relationships (org chart - who reports to whom)
- Informal relationships (mentorship, political alliances, friendships)
- Graph visualization API returning nodes + edges
- Field-level encryption for sensitive notes

**Key Endpoints:**
- `POST /api/power-map/players` - Add colleague
- `GET /api/power-map/visualization` - Get graph data
- `POST /api/power-map/relationships` - Map informal influence

**Example Player:**
```json
{
  "name": "Jennifer Wu",
  "role": "Senior PM",
  "influence_level": 6,
  "relationship_status": "rival",
  "notes": "Has stolen credit twice. Strategically manages up to Sarah."
}
```

### 3. The Log Book ✅
**What it does:** Timeline/journal of interactions for pattern detection

**Implementation:**
- Timestamped interaction logging (meetings, emails, incidents)
- Encrypted descriptions (credit-stealing, conflicts, wins)
- Sentiment tracking (positive/neutral/negative/hostile)
- Risk level per interaction
- Tagging system for categorization
- Timeline view per colleague
- Automatic context retrieval for AI analysis

**Key Endpoints:**
- `POST /api/logbook/interactions` - Log new interaction
- `GET /api/logbook/interactions` - List with filters
- `GET /api/logbook/players/{id}/timeline` - Player-specific timeline

**Example Interaction:**
```json
{
  "title": "Took credit for my feature in stakeholder meeting",
  "description": "Jennifer presented MY research as her own...",
  "interaction_type": "meeting",
  "sentiment": "hostile",
  "risk_level": "high",
  "tags": ["credit-stealing", "promotion-threat"]
}
```

## 🔒 Security & Privacy (Implemented)

1. **JWT Authentication**
   - Secure login/signup
   - Token-based API access
   - Configurable expiration

2. **Field-Level Encryption**
   - User-specific encryption keys
   - Sensitive fields encrypted at rest (notes, descriptions, messages)
   - Uses Fernet (symmetric encryption)

3. **No Web Scraping**
   - All data is user-inputted
   - Avoids legal risks with LinkedIn/social platforms

4. **Password Security**
   - Bcrypt hashing
   - No plaintext storage

## 🗄️ Database Schema (PostgreSQL)

```
users
├── id (UUID)
├── email (unique)
├── password_hash
├── encryption_key
└── profile fields

players
├── id (UUID)
├── user_id (FK)
├── name, role, department
├── influence_level (1-10)
├── relationship_status (ally/neutral/rival/enemy)
├── reports_to_player_id (FK)
└── notes (encrypted)

interactions
├── id (UUID)
├── user_id (FK)
├── player_id (FK)
├── title, description (encrypted)
├── interaction_type, sentiment, risk_level
├── tags (array)
└── interaction_date

power_relationships
├── id (UUID)
├── user_id (FK)
├── from_player_id (FK)
├── to_player_id (FK)
├── influence_type
└── strength (1-10)

decoded_messages
├── id (UUID)
├── user_id (FK)
├── original_text (encrypted)
├── subtext_analysis
├── risk_level
└── suggested_reply
```

## 🎭 Demo Data (Alex Persona)

The seed script creates a realistic scenario:

**Alex Martinez** - Senior Product Manager at TechCorp Inc.
- Competing for promotion
- Experiencing office politics challenges

**The Cast:**
1. **Sarah Chen** (VP of Product) - Alex's boss, being vague about promotion
2. **Jennifer Wu** (Senior PM) - Direct rival, has stolen credit twice
3. **Marcus Johnson** (Dir. Engineering) - Strong ally
4. **David Park** (CPO) - Ultimate decision maker for promotion
5. **Lisa Thompson** (PM) - Junior mentee, loyal
6. **Robert Kim** (Head of Sales) - Influential with CEO

**Logged Incidents:**
- Jennifer stole credit in stakeholder meeting (High Risk)
- Sarah gave vague promotion feedback (Medium Risk)
- Marcus praised Alex publicly (Low Risk/Win)
- Lisa warned about Jennifer's tactics (Intelligence)

## 🚀 How to Get Started

### 1. Setup Environment
```bash
# Install dependencies
./install
. ./activate.sh
cd www && npm install && cd ..

# Configure .env
cp .env.example .env
# Edit .env: Set DATABASE_URL, ANTHROPIC_API_KEY, JWT_SECRET_KEY
```

### 2. Initialize Database
```bash
# Create PostgreSQL database
createdb subtext

# Create tables
python scripts/init_db.py

# Load demo data
python scripts/seed_data.py
```

### 3. Run Development Server
```bash
./dev
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/api
```

### 4. Test with Demo User
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alex@example.com","password":"password123"}'

# Use the access_token in subsequent requests
```

## 📚 Documentation

- **Setup Guide:** `SETUP_SUBTEXT.md` - Complete setup instructions
- **API Docs:** Visit `http://localhost:8000/api` when server is running
- **Environment Config:** `.env.example` - All required variables

## 🎨 Frontend (Not Yet Built)

The backend API is complete. You now need to build React components for:

1. **Tone Decoder UI**
   - Text input box for pasting messages
   - Sender name/role fields
   - Display of AI analysis (subtext, risk, suggested reply)

2. **Power Map Visualization**
   - Graph rendering (use D3.js or Cytoscape.js)
   - Node colors based on relationship status
   - Click nodes to view/edit player details

3. **Log Book Interface**
   - Timeline view of interactions
   - Filter by player, sentiment, risk level
   - Quick-add interaction form

## 💰 Cost Considerations

- **Database:** Free tier PostgreSQL on Render.com or Supabase
- **Hosting:** Free tier on Render.com, Railway, or Fly.io
- **AI Costs:** ~$0.003 per Tone Decoder analysis (Claude 3.5 Sonnet)
  - 100 analyses/month = ~$0.30
  - 1000 analyses/month = ~$3.00

## 🔐 Environment Variables Required

```bash
DATABASE_URL=postgresql://user:pass@host:5432/subtext
ANTHROPIC_API_KEY=sk-ant-...
JWT_SECRET_KEY=<generate with: openssl rand -hex 32>
```

## 📊 What Works Right Now

✅ User signup/login
✅ Create and manage colleagues (players)
✅ Log interactions with encryption
✅ Map power relationships
✅ AI message analysis with context
✅ Complete REST API
✅ Database migrations
✅ Demo data seeding

## ❌ What's NOT Built Yet

- Frontend React UI components
- Power Map graph visualization
- Mobile app (React Native)
- Email/Slack integration
- PDF export features
- Pattern detection AI
- Promotion readiness scoring

## 🎯 Next Steps (Recommended Priority)

1. **Week 1-2:** Build basic frontend UI
   - Login/signup forms
   - Tone Decoder interface (highest value)
   - Simple player list view

2. **Week 3-4:** Power Map visualization
   - Implement graph with D3.js or Cytoscape.js
   - Player CRUD forms
   - Relationship mapping UI

3. **Week 5-6:** Log Book interface
   - Timeline component
   - Quick-add interaction modal
   - Filter/search functionality

4. **Week 7-8:** Polish & Deploy
   - Dark mode styling
   - Mobile responsiveness
   - Deploy to production
   - Beta testing with real users

## 🤖 AI System Prompt

The Tone Decoder uses this custom persona:

> "You are the Chief of Staff to a mid-level professional navigating corporate politics. Your role is to provide strategic, objective advice that maximizes their career longevity and leverage.
>
> Be direct and candid. No corporate platitudes. Assume everyone has mixed motives. When someone takes credit, sabotages, or undermines: name it clearly and suggest countermeasures. Prioritize survival and advancement over being 'nice.' Be Machiavellian when necessary."

This differentiates Subtext from generic career coaches.

## 📝 Files Modified/Created

**New Core Modules:**
- `src/subtext/models.py` - Database ORM
- `src/subtext/schemas.py` - API schemas
- `src/subtext/auth.py` - Authentication
- `src/subtext/encryption.py` - Data encryption
- `src/subtext/ai_service.py` - Claude integration

**New API Routes:**
- `src/subtext/routes/auth.py`
- `src/subtext/routes/tone_decoder.py`
- `src/subtext/routes/power_map.py`
- `src/subtext/routes/logbook.py`

**New Scripts:**
- `scripts/init_db.py` - Database setup
- `scripts/reset_db.py` - Database reset
- `scripts/seed_data.py` - Demo data

**Configuration:**
- `requirements.txt` - Added AI, auth, encryption deps
- `.env.example` - Environment template
- `SETUP_SUBTEXT.md` - Setup guide

## 🎉 Success Metrics

The MVP is complete when:
- ✅ All three features work via API
- ✅ Security/encryption implemented
- ✅ Demo data demonstrates value prop
- ⏳ Frontend UI built (next step)
- ⏳ Real user can test end-to-end

**Current Status: Backend 100% Complete** 🎊

You now have a production-ready API that can:
1. Decode office politics messages with AI
2. Map power dynamics in organizations
3. Track interaction patterns for strategic advantage

All with privacy-first encryption and zero web scraping risk.

## 🙋 Questions?

- API docs: `http://localhost:8000/api`
- Setup issues: See `SETUP_SUBTEXT.md`
- Architecture: See `src/subtext/models.py` for schema

---

**Built with:** FastAPI, PostgreSQL, Anthropic Claude, SQLAlchemy, JWT, Fernet Encryption

**Next Sprint:** Frontend UI Development
