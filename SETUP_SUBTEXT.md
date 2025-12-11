# Subtext - Pocket Chief of Staff Setup Guide

## Project Overview

**Subtext** is a strategic career navigation app for mid-level professionals. It helps users:
- Decode ambiguous communications (Tone Decoder)
- Map office power dynamics (Power Map)
- Track interactions for strategic context (Log Book)

## Tech Stack

**Backend:**
- FastAPI (Python)
- PostgreSQL database
- SQLAlchemy ORM
- Anthropic Claude 3.5 Sonnet (AI)
- JWT authentication
- Field-level encryption for sensitive data

**Frontend:**
- React + TypeScript
- Webpack dev server

## Prerequisites

1. **Python 3.7+** installed
2. **Node.js 14+** and npm installed
3. **PostgreSQL** database running
4. **Anthropic API key** (get from console.anthropic.com)

## Initial Setup

### 1. Install Dependencies

```bash
# Install Python dependencies
./install

# Activate virtual environment
. ./activate.sh

# Install frontend dependencies
cd www && npm install && cd ..
```

### 2. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env and set:
nano .env
```

Required variables:
- `DATABASE_URL` - PostgreSQL connection string
- `ANTHROPIC_API_KEY` - Your Anthropic API key
- `JWT_SECRET_KEY` - Random secret for JWT (generate with `openssl rand -hex 32`)

### 3. Setup PostgreSQL Database

**Option A: Local PostgreSQL**
```bash
# Create database
createdb subtext

# Or using psql
psql -c "CREATE DATABASE subtext;"
```

**Option B: Use Render.com (Cloud)**
1. Create free PostgreSQL instance at render.com
2. Copy the External Database URL
3. Set `DATABASE_URL` in `.env`

### 4. Initialize Database

```bash
# Create all tables
python scripts/init_db.py

# Seed with demo data (Alex persona + colleagues)
python scripts/seed_data.py
```

This creates:
- Demo user: `alex@example.com` / `password123`
- 6 colleagues in Alex's org
- 5 sample interactions logged
- Power relationship mappings

## Running the Application

### Development Mode

```bash
# Start both backend and frontend dev servers
./dev
```

This runs:
- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:4999`
- API Docs: `http://localhost:8000/api`

### Production Mode

```bash
# Build frontend and run production server
./prod
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login (returns JWT token)
- `GET /api/auth/me` - Get current user info

### Tone Decoder (Feature A)
- `POST /api/tone-decoder/analyze` - Analyze a message for subtext
- `GET /api/tone-decoder/history` - Get analysis history

### Power Map (Feature B)
- `POST /api/power-map/players` - Create new player (colleague)
- `GET /api/power-map/players` - List all players
- `GET /api/power-map/players/{id}` - Get player details
- `PATCH /api/power-map/players/{id}` - Update player
- `DELETE /api/power-map/players/{id}` - Delete player
- `POST /api/power-map/relationships` - Create power relationship
- `GET /api/power-map/visualization` - Get graph data (nodes + edges)

### Log Book (Feature C)
- `POST /api/logbook/interactions` - Log new interaction
- `GET /api/logbook/interactions` - List interactions (with filters)
- `GET /api/logbook/interactions/{id}` - Get interaction details
- `PATCH /api/logbook/interactions/{id}` - Update interaction
- `DELETE /api/logbook/interactions/{id}` - Delete interaction
- `GET /api/logbook/players/{id}/timeline` - Get player timeline

## Testing the MVP

### 1. Login as Alex
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alex@example.com","password":"password123"}'
```

Copy the `access_token` from response.

### 2. Use Tone Decoder

```bash
curl -X POST http://localhost:8000/api/tone-decoder/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "original_text": "Hey Alex, we need to chat about your Q4 roadmap. Do you have time this week?",
    "sender_name": "Jennifer Wu",
    "sender_role": "Senior PM"
  }'
```

The AI will return:
- Subtext analysis (what they're REALLY saying)
- Risk level (low/medium/high)
- Suggested strategic response
- Follow-up actions

### 3. View Power Map

```bash
curl -X GET http://localhost:8000/api/power-map/visualization \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Returns graph structure with nodes (colleagues) and edges (relationships).

### 4. View Log Book

```bash
curl -X GET http://localhost:8000/api/logbook/interactions \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Architecture Notes

### Data Security

1. **Field Encryption**: Sensitive fields (notes, descriptions, messages) are encrypted at rest using Fernet (symmetric encryption)
2. **User-Specific Keys**: Each user has their own encryption key stored in database
3. **JWT Authentication**: All API routes require valid JWT token
4. **PostgreSQL RLS**: Row-level security ensures users only access their own data

### AI System Prompt

The Tone Decoder uses a custom system prompt that enforces a "Chief of Staff" persona:
- Strategic and objective (not cheerleader HR)
- Machiavellian when necessary
- Analyzes power dynamics ruthlessly
- Prioritizes career survival and advancement

Located in: `src/subtext/ai_service.py`

### Database Schema

See `src/subtext/models.py` for full schema:
- `users` - User accounts with encryption keys
- `players` - Colleagues/stakeholders
- `interactions` - Log book entries (encrypted)
- `power_relationships` - Informal influence mapping
- `decoded_messages` - Tone analysis cache

## Database Management

```bash
# Reset database (WARNING: deletes all data!)
python scripts/reset_db.py

# Re-seed demo data
python scripts/seed_data.py
```

## Next Steps for Production

1. **Frontend Development**: Build React UI components for:
   - Tone Decoder form
   - Power Map visualization (D3.js or Cytoscape.js)
   - Log Book timeline view

2. **Security Hardening**:
   - Change `JWT_SECRET_KEY` to strong random value
   - Enable HTTPS in production
   - Consider client-side encryption for extra privacy

3. **Deployment**:
   - Deploy backend to Render.com / Railway / Fly.io
   - Use managed PostgreSQL (Render.com / Supabase)
   - Deploy frontend to Vercel / Netlify

4. **Features to Add**:
   - Email/Slack integration for automatic logging
   - Export power map as PDF
   - AI-powered insights on promotion readiness
   - Pattern detection across interactions

## Troubleshooting

### Database connection errors
- Verify PostgreSQL is running: `pg_isready`
- Check `DATABASE_URL` in `.env`
- Ensure database exists: `psql -l | grep subtext`

### AI analysis fails
- Verify `ANTHROPIC_API_KEY` is set correctly
- Check API quota at console.anthropic.com
- Review logs in `data/logs/system.log`

### Import errors
- Ensure virtual environment is activated: `. ./activate.sh`
- Reinstall dependencies: `./install`

## Demo Scenario

The seed data creates a realistic office politics scenario for Alex:

**The Situation:**
- Alex is a Senior PM competing for promotion
- Jennifer Wu (rival) has stolen credit twice
- Sarah Chen (boss) is being vague about promotion
- Marcus Johnson (ally) is supportive
- David Park (CPO) needs more exposure to Alex's work

**Try This:**
1. Log in as Alex
2. Use Tone Decoder on Jennifer's messages
3. View the Power Map to see influence relationships
4. Check Log Book for historical patterns
5. Get strategic advice on how to handle the credit-stealing

## License

Private project - do not distribute
