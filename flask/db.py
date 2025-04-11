import sqlite3
import os
from datetime import datetime

# مسیر دیتابیس
DB_PATH = os.path.join(os.path.dirname(__file__), 'chatbot.db')

def init_db():
    """ایجاد دیتابیس و جداول مورد نیاز"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # جدول مکالمات
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        tenant_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # جدول پیام‌ها
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER NOT NULL,
        sender TEXT NOT NULL,
        message TEXT NOT NULL,
        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES conversations (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def save_message(session_id, tenant_id, user_id, sender, message):
    """ذخیره پیام در دیتابیس"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # بررسی وجود مکالمه
    cursor.execute(
        "SELECT id FROM conversations WHERE session_id = ? AND tenant_id = ? AND user_id = ?", 
        (session_id, tenant_id, user_id)
    )
    result = cursor.fetchone()
    
    if result:
        conversation_id = result[0]
    else:
        # ایجاد مکالمه جدید
        cursor.execute(
            "INSERT INTO conversations (session_id, tenant_id, user_id) VALUES (?, ?, ?)",
            (session_id, tenant_id, user_id)
        )
        conversation_id = cursor.lastrowid
    
    # ذخیره پیام
    cursor.execute(
        "INSERT INTO messages (conversation_id, sender, message) VALUES (?, ?, ?)",
        (conversation_id, sender, message)
    )
    
    conn.commit()
    conn.close()
    
    return True

def get_conversation_history(session_id, tenant_id, user_id, limit=10):
    """دریافت تاریخچه مکالمه"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT m.sender, m.message, m.sent_at
        FROM messages m
        JOIN conversations c ON m.conversation_id = c.id
        WHERE c.session_id = ? AND c.tenant_id = ? AND c.user_id = ?
        ORDER BY m.sent_at DESC
        LIMIT ?
        """,
        (session_id, tenant_id, user_id, limit)
    )
    
    result = cursor.fetchall()
    conn.close()
    
    # برگرداندن نتیجه به صورت لیستی از دیکشنری‌ها
    history = [
        {"sender": row[0], "message": row[1], "timestamp": row[2]}
        for row in result
    ]
    
    return history[::-1]  # معکوس کردن برای نمایش قدیمی‌ترین پیام‌ها اول