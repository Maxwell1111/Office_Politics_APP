# Politico - Office Politics Navigator
## Backend Features Implemented

### 🎯 Core Philosophy: "Corporate Zen"
- Calm, strategic, objective, and supportive
- Does NOT encourage toxic behavior
- Helps users protect themselves and communicate effectively
- Privacy-first design

---

## ✅ IMPLEMENTED FEATURES

### 1. 🤖 AI Scenario Analyzer
**Endpoint:** `POST /api/analyze-scenario`

**What it does:**
- Analyzes complex office politics situations
- Identifies power dynamics
- Assesses risk level (Low/Medium/High/Critical)
- Provides 3 strategic options:
  1. **Passive**: Low-confrontation approach
  2. **Assertive**: Professional boundary-setting
  3. **Strategic**: Long-term alliance building

**Request:**
```json
{
  "scenario_description": "My manager took credit for my project...",
  "stakeholders_involved": ["Manager", "VP"],
  "user_goal": "Get recognition without creating conflict"
}
```

**Response:**
```json
{
  "power_dynamic": "Your manager holds positional power...",
  "risk_level": "medium",
  "political_implications": "This could affect future opportunities...",
  "strategy_options": [
    {
      "strategy_type": "passive",
      "title": "Document and Wait",
      "description": "...",
      "pros": ["Low risk", "Gather evidence"],
      "cons": ["Slow", "May miss opportunities"],
      "recommended_actions": ["Keep detailed records", "Build rapport with VP"]
    },
    // ... assertive and strategic options
  ]
}
```

---

### 2. 📧 Email Tone Analyzer & Rewriter
**Endpoint:** `POST /api/analyze-tone`

**What it does:**
- Analyzes email drafts for aggressive or passive language
- Scores aggression (0-100) and passivity (0-100)
- Explains political implications
- Provides rewrite using Non-Violent Communication (NVC)

**Request:**
```json
{
  "email_draft": "I can't believe you did this again..."
}
```

**Response:**
```json
{
  "aggression_score": 85,
  "passivity_score": 10,
  "political_implications": "This tone could escalate conflict and damage relationship",
  "suggested_rewrite": "I noticed this pattern has occurred twice. Could we discuss how to prevent this in the future?"
}
```

---

### 3. 👥 Stakeholder Tracking System
**Endpoints:** `/api/stakeholders/*`

**What it does:**
- Track people in your organization
- Rate their influence (1-10)
- Define relationship status (Ally/Neutral/Adversary/Unknown)
- Record core motivations
- Add encrypted private notes (even admins can't read them!)
- Log interaction history with encryption

**Features:**
- `POST /api/stakeholders` - Create stakeholder
- `GET /api/stakeholders` - List all
- `GET /api/stakeholders/{id}/notes-decrypted` - Decrypt notes (separate endpoint for security)
- `POST /api/stakeholders/{id}/interactions` - Log interaction
- `GET /api/stakeholders/{id}/interactions` - View history

**Stakeholder Model:**
```json
{
  "name": "Jane Smith",
  "role": "VP of Engineering",
  "relationship_status": "neutral",
  "influence_level": 9,
  "core_motivations": ["Recognition", "Autonomy", "Innovation"],
  "notes_encrypted": "[ENCRYPTED]"
}
```

---

### 4. 🔐 Security & Privacy Features

**Encryption Service:**
- Fernet symmetric encryption for all sensitive data
- Master key stored in environment variable `ENCRYPTION_MASTER_KEY`
- Notes and interaction logs automatically encrypted
- Even database admins cannot read private notes

**Input Sanitization:**
- All user input sanitized to prevent XSS attacks
- Removes dangerous HTML/JavaScript patterns
- Protects against code injection

**Functions:**
- `encrypt_text(plaintext)` → encrypted string
- `decrypt_text(encrypted)` → plaintext
- `sanitize_input(text)` → clean text

---

## 🏗️ ARCHITECTURE

### Models & Data Structure

**New Enums:**
- `RelationshipStatus`: ally, neutral, adversary, unknown
- `RiskLevel`: low, medium, high, critical
- `StrategyType`: passive, assertive, strategic

**New Models:**
- `Stakeholder` - People to track politically
- `InteractionLog` - History of interactions
- `ScenarioAnalysis` - AI analysis results
- `ToneAnalysis` - Email tone analysis
- `StrategyOption` - Strategic approach option

### LLM Integration

**Service:** `PoliticoLLMService`
- Uses Anthropic Claude (claude-3-5-sonnet-20241022)
- Falls back to mock responses if API key not set
- Structured prompts for consistent output
- JSON parsing with error handling

**Configuration:**
Set environment variable: `ANTHROPIC_API_KEY=your-key-here`

---

## 🚀 NEXT STEPS

### Frontend UI Needed:
1. **Scenario Analyzer Page**
   - Form: scenario description, stakeholders, goal
   - Display: power dynamics, risk level, 3 strategy cards

2. **Tone Checker Page**
   - Textarea for email draft
   - Display: scores, implications, suggested rewrite
   - Side-by-side comparison

3. **Stakeholder Dashboard**
   - List view with filters (Allies, Adversaries, etc.)
   - Add/edit stakeholder forms
   - Interaction timeline
   - Encrypted notes with decrypt button

4. **Update Branding**
   - Rename "Office Politics" → "Politico"
   - Update colors, logo, messaging
   - Consistent "Corporate Zen" tone

### Database Migration:
- Replace in-memory storage with PostgreSQL
- Encrypted columns for sensitive data
- User authentication & multi-tenancy
- Data retention policy (auto-delete after 30 days option)

---

## 📊 API SUMMARY

### Working Endpoints:
- ✅ `/api/health` - Health check
- ✅ `/api/power-maps/*` - Power mapping
- ✅ `/api/stakeholders/*` - Stakeholder tracking
- ✅ `/api/analyze-scenario` - AI scenario analysis
- ✅ `/api/analyze-tone` - Email tone checking
- ✅ `/api/analyzer/test` - Test LLM connection

### Testing:
```bash
# Test scenario analyzer
curl -X POST https://your-app.onrender.com/api/analyze-scenario \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_description": "My coworker is undermining me in meetings",
    "stakeholders_involved": ["Coworker", "Manager"],
    "user_goal": "Stop the behavior professionally"
  }'

# Test tone analyzer
curl -X POST https://your-app.onrender.com/api/analyze-tone \
  -H "Content-Type: application/json" \
  -d '{
    "email_draft": "This is unacceptable and needs to stop immediately."
  }'
```

---

## 🎨 Design Principles

1. **Privacy First** - Encryption by default
2. **Corporate Zen** - Calm, strategic tone
3. **Non-Toxic** - Never encourage bad behavior
4. **Actionable** - Always provide concrete next steps
5. **Empowering** - Help users protect themselves
6. **Professional** - Maintain workplace decorum

---

**Status:** Backend fully functional, ready for frontend integration
**Next:** Build UI components for these features
