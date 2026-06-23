import sqlite3
import json
import os
from typing import List, Optional

# Supports persistent disk on Render: set DATABASE_URL=/var/data/civicpulse.db
DB_PATH = os.environ.get("DATABASE_URL", "civicpulse.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            location_name TEXT,
            source_signals TEXT DEFAULT '[]',
            confidence_score INTEGER DEFAULT 0,
            confirmation_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'DISCOVERED',
            authority_name TEXT,
            authority_email TEXT,
            escalation_letter TEXT,
            escalation_sent_at TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS confirmations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            issue_id INTEGER REFERENCES issues(id),
            photo_url TEXT,
            gemini_validation TEXT,
            validation_passed INTEGER DEFAULT 0,
            citizen_note TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS escalations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            issue_id INTEGER REFERENCES issues(id),
            authority_name TEXT,
            authority_email TEXT,
            letter_content TEXT,
            sent_at TEXT,
            email_status TEXT DEFAULT 'PENDING'
        );
    """)
    conn.commit()
    conn.close()

def seed_issue(data: dict) -> int:
    """Insert a pre-defined demo issue with any status (first-run seeding only)."""
    conn = get_db()
    cursor = conn.execute("""
        INSERT INTO issues (title, category, description, latitude, longitude,
            location_name, source_signals, confidence_score, confirmation_count,
            status, authority_name, authority_email, escalation_letter, escalation_sent_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["title"], data["category"], data["description"],
        data["latitude"], data["longitude"], data.get("location_name", ""),
        json.dumps(data.get("source_signals", [])),
        data.get("confidence_score", 10),
        data.get("confirmation_count", 0),
        data.get("status", "DISCOVERED"),
        data.get("authority_name"),
        data.get("authority_email"),
        data.get("escalation_letter"),
        data.get("escalation_sent_at"),
    ))
    conn.commit()
    issue_id = cursor.lastrowid
    conn.close()
    return issue_id

def create_issue(data: dict) -> int:
    conn = get_db()
    cursor = conn.execute("""
        INSERT INTO issues (title, category, description, latitude, longitude,
            location_name, source_signals, confidence_score, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'DISCOVERED')
    """, (
        data["title"], data["category"], data["description"],
        data["latitude"], data["longitude"], data.get("location_name", ""),
        json.dumps(data.get("source_signals", [])), data.get("confidence_score", 10)
    ))
    conn.commit()
    issue_id = cursor.lastrowid
    conn.close()
    return issue_id

def get_all_issues(status: Optional[str] = None) -> List[dict]:
    conn = get_db()
    if status:
        rows = conn.execute(
            "SELECT * FROM issues WHERE status = ? ORDER BY confidence_score DESC", (status,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM issues ORDER BY confidence_score DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_issue(issue_id: int) -> Optional[dict]:
    conn = get_db()
    row = conn.execute("SELECT * FROM issues WHERE id = ?", (issue_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def add_confirmation(issue_id: int, data: dict) -> None:
    conn = get_db()
    conn.execute("""
        INSERT INTO confirmations (issue_id, photo_url, gemini_validation, validation_passed, citizen_note)
        VALUES (?, ?, ?, ?, ?)
    """, (
        issue_id, data.get("photo_url", ""), data.get("gemini_validation", ""),
        1 if data.get("validation_passed") else 0, data.get("citizen_note", "")
    ))
    conn.execute("""
        UPDATE issues
        SET confirmation_count = confirmation_count + 1,
            confidence_score = confidence_score + 15,
            status = CASE WHEN confirmation_count + 1 >= 5 THEN 'CONFIRMED' ELSE status END,
            updated_at = datetime('now')
        WHERE id = ?
    """, (issue_id,))
    conn.commit()
    conn.close()

def update_issue_escalated(issue_id: int, authority_name: str, authority_email: str, letter: str) -> None:
    conn = get_db()
    conn.execute("""
        UPDATE issues
        SET status = 'ESCALATED', authority_name = ?, authority_email = ?,
            escalation_letter = ?, escalation_sent_at = datetime('now'),
            updated_at = datetime('now')
        WHERE id = ?
    """, (authority_name, authority_email, letter, issue_id))
    conn.commit()
    conn.close()

def get_issues_ready_for_escalation() -> List[dict]:
    conn = get_db()
    rows = conn.execute("""
        SELECT * FROM issues
        WHERE status = 'CONFIRMED' AND escalation_sent_at IS NULL
        ORDER BY confidence_score DESC
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_stats() -> dict:
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM issues").fetchone()[0]
    discovered = conn.execute("SELECT COUNT(*) FROM issues WHERE status='DISCOVERED'").fetchone()[0]
    confirmed = conn.execute("SELECT COUNT(*) FROM issues WHERE status='CONFIRMED'").fetchone()[0]
    escalated = conn.execute("SELECT COUNT(*) FROM issues WHERE status='ESCALATED'").fetchone()[0]
    resolved = conn.execute("SELECT COUNT(*) FROM issues WHERE status='RESOLVED'").fetchone()[0]
    total_confirmations = conn.execute("SELECT COUNT(*) FROM confirmations").fetchone()[0]
    conn.close()
    return {
        "total_issues": total,
        "discovered": discovered,
        "confirmed": confirmed,
        "escalated": escalated,
        "resolved": resolved,
        "total_citizen_confirmations": total_confirmations,
    }
