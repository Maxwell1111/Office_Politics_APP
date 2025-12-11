#!/usr/bin/env python3
"""
Seed script to populate database with demo data.

Creates a demo user "Alex" (the target persona) with:
- A power map of colleagues
- Sample interactions logged
- Power relationships mapped

Usage:
    python scripts/seed_data.py
"""

import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from subtext.db import SessionLocal
from subtext.models import User, Player, Interaction, PowerRelationship
from subtext.auth import hash_password
from subtext.encryption import EncryptionService


def create_demo_user(db):
    """Create demo user 'Alex'"""
    print("👤 Creating demo user 'Alex'...")

    # Check if user exists
    existing = db.query(User).filter(User.email == "alex@example.com").first()
    if existing:
        print("   ℹ️  User already exists, using existing user")
        return existing

    encryption_key = EncryptionService.generate_key()
    user = User(
        email="alex@example.com",
        password_hash=hash_password("password123"),
        full_name="Alex Martinez",
        current_role="Senior Product Manager",
        company="TechCorp Inc.",
        encryption_key=encryption_key
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    print(f"   ✅ Created user: {user.email}")
    print(f"   🔑 Password: password123")
    return user


def create_demo_players(db, user):
    """Create demo colleagues for Alex's power map"""
    print("\n🎭 Creating demo players (colleagues)...")

    players_data = [
        {
            "name": "Sarah Chen",
            "role": "VP of Product",
            "department": "Product",
            "influence_level": 9,
            "relationship_status": "neutral",
            "reports_to": None,
            "notes": "Direct boss. Very political. Always looks out for her own career first. "
                     "Has been non-committal about my promotion prospects."
        },
        {
            "name": "Marcus Johnson",
            "role": "Director of Engineering",
            "department": "Engineering",
            "influence_level": 8,
            "relationship_status": "ally",
            "reports_to": None,
            "notes": "Strong ally. We collaborated on the Q3 launch. He respects my work and "
                     "has vouched for me in leadership meetings."
        },
        {
            "name": "Jennifer Wu",
            "role": "Senior PM",
            "department": "Product",
            "influence_level": 6,
            "relationship_status": "rival",
            "reports_to": None,  # Will be set to Sarah
            "notes": "Direct competitor for the next promotion. Has tried to take credit for my "
                     "customer research twice. Very strategic about visibility with executives."
        },
        {
            "name": "David Park",
            "role": "Chief Product Officer",
            "department": "Product",
            "influence_level": 10,
            "relationship_status": "unknown",
            "reports_to": None,
            "notes": "Sarah's boss. Makes final decisions on promotions. Have only met him in "
                     "all-hands meetings. Needs more exposure to my work."
        },
        {
            "name": "Lisa Thompson",
            "role": "PM",
            "department": "Product",
            "influence_level": 5,
            "relationship_status": "ally",
            "reports_to": None,  # Will be set to Sarah
            "notes": "Junior PM I mentor. Loyal and appreciates my guidance. Good source of "
                     "information about team dynamics."
        },
        {
            "name": "Robert Kim",
            "role": "Head of Sales",
            "department": "Sales",
            "influence_level": 7,
            "relationship_status": "neutral",
            "reports_to": None,
            "notes": "Influential with CEO. Loves product features that drive immediate revenue. "
                     "Could be won over with the right pitch."
        }
    ]

    created_players = {}

    for data in players_data:
        # Encrypt notes
        encrypted_notes = EncryptionService.encrypt(data["notes"], user.encryption_key)

        player = Player(
            user_id=user.id,
            name=data["name"],
            role=data["role"],
            department=data["department"],
            influence_level=data["influence_level"],
            relationship_status=data["relationship_status"],
            notes=encrypted_notes
        )

        db.add(player)
        db.commit()
        db.refresh(player)

        created_players[data["name"]] = player
        print(f"   ✅ Created player: {data['name']} ({data['role']})")

    # Set reporting relationships
    created_players["Sarah Chen"].reports_to_player_id = created_players["David Park"].id
    created_players["Jennifer Wu"].reports_to_player_id = created_players["Sarah Chen"].id
    created_players["Lisa Thompson"].reports_to_player_id = created_players["Sarah Chen"].id

    db.commit()

    return created_players


def create_demo_interactions(db, user, players):
    """Create sample logged interactions"""
    print("\n📝 Creating demo interactions...")

    interactions_data = [
        {
            "player_name": "Jennifer Wu",
            "title": "Took credit for my feature in stakeholder meeting",
            "description": "During the product review with David Park, Jennifer presented MY customer "
                          "research findings as if they were her own work. She said 'I discovered that users...' "
                          "when referring to interviews I conducted. I had shared the raw data with her in good "
                          "faith for feedback. David seemed impressed and asked her follow-up questions. "
                          "I didn't correct her in the moment (didn't want to seem petty), but this is the second time.",
            "interaction_type": "meeting",
            "sentiment": "hostile",
            "risk_level": "high",
            "tags": ["credit-stealing", "promotion-threat", "stakeholder-visibility"],
            "days_ago": 3
        },
        {
            "player_name": "Sarah Chen",
            "title": "Vague feedback on promotion timeline",
            "description": "Asked Sarah about promotion timeline in our 1:1. She said 'we'll see how things go' "
                          "and 'you need more exec visibility' but was very non-specific about what that means. "
                          "She seemed distracted and ended the meeting 10 minutes early. This is the third time "
                          "she's dodged the promotion question.",
            "interaction_type": "meeting",
            "sentiment": "negative",
            "risk_level": "medium",
            "tags": ["promotion-related", "vague-feedback", "career-growth"],
            "days_ago": 5
        },
        {
            "player_name": "Marcus Johnson",
            "title": "Positive feedback on API redesign collaboration",
            "description": "Marcus thanked me in the engineering all-hands for the API requirements doc. "
                          "He said it was 'the most thorough and well-thought-out spec he's seen in years' and "
                          "that it saved his team 2 weeks of rework. He cc'd Sarah and David on the follow-up email.",
            "interaction_type": "email",
            "sentiment": "positive",
            "risk_level": "low",
            "tags": ["win", "stakeholder-visibility", "cross-functional"],
            "days_ago": 10
        },
        {
            "player_name": "Jennifer Wu",
            "title": "First credit-stealing incident - Q2 roadmap",
            "description": "Jennifer presented my Q2 roadmap ideas to Sarah as her own during planning session. "
                          "When I brought it up privately, she said 'oh I thought those were from the brainstorm, "
                          "I didn't realize you were claiming them.' Gaslighting. Made mental note to document everything.",
            "interaction_type": "meeting",
            "sentiment": "hostile",
            "risk_level": "high",
            "tags": ["credit-stealing", "gaslighting", "documentation-needed"],
            "days_ago": 45
        },
        {
            "player_name": "Lisa Thompson",
            "title": "Lisa warned me about Jennifer's tactics",
            "description": "During coffee chat, Lisa mentioned that Jennifer has been asking Sarah for more "
                          "'stretch projects' and angling for promotion. Lisa said Jennifer explicitly asked her "
                          "not to mention this to me. Lisa is loyal and gave me the heads up. Jennifer is making moves.",
            "interaction_type": "other",
            "sentiment": "neutral",
            "risk_level": "medium",
            "tags": ["intelligence", "promotion-threat", "office-politics"],
            "days_ago": 7
        }
    ]

    for data in interactions_data:
        player = players[data["player_name"]]
        interaction_date = datetime.now() - timedelta(days=data["days_ago"])

        # Encrypt description
        encrypted_desc = EncryptionService.encrypt(data["description"], user.encryption_key)

        interaction = Interaction(
            user_id=user.id,
            player_id=player.id,
            title=data["title"],
            description=encrypted_desc,
            interaction_type=data["interaction_type"],
            sentiment=data["sentiment"],
            risk_level=data["risk_level"],
            tags=data["tags"],
            interaction_date=interaction_date
        )

        db.add(interaction)
        print(f"   ✅ Created interaction: {data['title']}")

    db.commit()


def create_demo_power_relationships(db, user, players):
    """Create informal influence relationships"""
    print("\n🔗 Creating power relationships...")

    relationships_data = [
        {
            "from": "Sarah Chen",
            "to": "David Park",
            "influence_type": "reports-to-and-political-alignment",
            "strength": 8,
            "notes": "Sarah carefully manages up to David. Always aligns her messaging with his priorities."
        },
        {
            "from": "Jennifer Wu",
            "to": "Sarah Chen",
            "influence_type": "strategic-flattery",
            "strength": 7,
            "notes": "Jennifer constantly praises Sarah and mirrors her opinions in meetings."
        },
        {
            "from": "Robert Kim",
            "to": "David Park",
            "influence_type": "peer-influence",
            "strength": 9,
            "notes": "Robert and David are golf buddies. Robert's opinion carries weight with David."
        },
        {
            "from": "Marcus Johnson",
            "to": "David Park",
            "influence_type": "respected-peer",
            "strength": 7,
            "notes": "David trusts Marcus's technical judgment. They worked together at previous company."
        }
    ]

    for data in relationships_data:
        relationship = PowerRelationship(
            user_id=user.id,
            from_player_id=players[data["from"]].id,
            to_player_id=players[data["to"]].id,
            influence_type=data["influence_type"],
            strength=data["strength"],
            notes=data["notes"]
        )

        db.add(relationship)
        print(f"   ✅ Created relationship: {data['from']} → {data['to']} ({data['influence_type']})")

    db.commit()


def main():
    """Run seed script"""
    print("🌱 Seeding Subtext database with demo data...\n")

    db = SessionLocal()

    try:
        # Create demo user
        user = create_demo_user(db)

        # Create players (colleagues)
        players = create_demo_players(db, user)

        # Create interactions (log book entries)
        create_demo_interactions(db, user, players)

        # Create power relationships
        create_demo_power_relationships(db, user, players)

        print("\n✅ Demo data seeded successfully!")
        print("\n📊 Summary:")
        print(f"   - User: alex@example.com (password: password123)")
        print(f"   - Players: {len(players)}")
        print(f"   - Interactions: 5")
        print(f"   - Power Relationships: 4")
        print("\n🚀 You can now:")
        print("   1. Start the dev server: ./dev")
        print("   2. Login as Alex at the UI")
        print("   3. Test the Tone Decoder with Jennifer's messages")
        print("   4. View the Power Map visualization")
        print("   5. Explore the Log Book timeline")

    except Exception as e:
        print(f"\n❌ Error seeding data: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
