import sqlite3
from datetime import datetime

DB_PATH = "data/tickets.db"


def init_db():
    """Create tickets table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            description TEXT,
            priority    TEXT NOT NULL,
            status      TEXT NOT NULL DEFAULT 'Open',
            assigned_to TEXT,
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def create_ticket(title, description, priority, assigned_to):
    """Create a new support ticket."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO tickets (title, description, priority, status, assigned_to, created_at, updated_at)
        VALUES (?, ?, ?, 'Open', ?, ?, ?)
    """, (title, description, priority, assigned_to, now, now))
    conn.commit()
    ticket_id = c.lastrowid
    conn.close()
    return ticket_id


def get_all_tickets(status_filter=None, priority_filter=None):
    """Get all tickets with optional filters."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    query = "SELECT * FROM tickets WHERE 1=1"
    params = []
    if status_filter and status_filter != "All":
        query += " AND status = ?"
        params.append(status_filter)
    if priority_filter and priority_filter != "All":
        query += " AND priority = ?"
        params.append(priority_filter)
    query += " ORDER BY created_at DESC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return rows


def update_ticket_status(ticket_id, new_status):
    """Update the status of a ticket."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        UPDATE tickets SET status = ?, updated_at = ? WHERE id = ?
    """, (new_status, now, ticket_id))
    conn.commit()
    conn.close()


def delete_ticket(ticket_id):
    """Delete a ticket by ID."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
    conn.commit()
    conn.close()


def get_ticket_stats():
    """Get summary counts by status and priority."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT status, COUNT(*) FROM tickets GROUP BY status")
    status_counts = dict(c.fetchall())
    c.execute("SELECT priority, COUNT(*) FROM tickets GROUP BY priority")
    priority_counts = dict(c.fetchall())
    conn.close()
    return status_counts, priority_counts