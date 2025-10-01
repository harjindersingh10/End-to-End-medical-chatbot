import sqlite3
from datetime import datetime
import os

class MediBotDB:
    def __init__(self, db_path='medibot.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Chat history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                sources INTEGER DEFAULT 0
            )
        ''')
        
        # Medical knowledge base table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medical_kb (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                rating INTEGER,
                comment TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chat_history (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Populate initial medical knowledge
        self.populate_initial_data()
    
    def populate_initial_data(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM medical_kb")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Initial medical knowledge
        medical_data = [
            ("cold", "Common cold symptoms: runny nose, sore throat, cough, mild headache, sneezing. Rest and stay hydrated.", "symptoms"),
            ("fever", "Fever indicates infection. Rest, drink fluids, take paracetamol if needed. See doctor if over 39°C.", "symptoms"),
            ("headache", "Headaches can be from stress, dehydration, or tension. Rest, hydrate, consider pain relief.", "symptoms"),
            ("paracetamol", "Paracetamol reduces pain and fever. Adult dose: 500-1000mg every 4-6 hours. Max 4g daily.", "medication"),
            ("first aid", "Basic first aid: Check breathing, control bleeding, treat for shock, call emergency services.", "emergency"),
            ("diabetes", "Diabetes symptoms: excessive thirst, frequent urination, fatigue, blurred vision.", "condition"),
            ("hypertension", "High blood pressure often has no symptoms. Regular monitoring important.", "condition"),
            ("asthma", "Asthma symptoms: wheezing, shortness of breath, chest tightness, coughing.", "condition")
        ]
        
        cursor.executemany("INSERT INTO medical_kb (keyword, content, category) VALUES (?, ?, ?)", medical_data)
        conn.commit()
        conn.close()
    
    def save_chat(self, user_message, bot_response, sources=0, user_id=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_history (user_message, bot_response, sources, user_id) VALUES (?, ?, ?, ?)",
            (user_message, bot_response, sources, user_id)
        )
        chat_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return chat_id
    
    def get_chat_history(self, limit=50):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_message, bot_response, timestamp, sources FROM chat_history ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        history = cursor.fetchall()
        conn.close()
        return history
    
    def search_medical_kb(self, query):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT content FROM medical_kb WHERE keyword LIKE ? OR content LIKE ?",
            (f"%{query}%", f"%{query}%")
        )
        results = cursor.fetchall()
        conn.close()
        return [result[0] for result in results]
    
    def save_feedback(self, chat_id, rating, comment=""):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO feedback (chat_id, rating, comment) VALUES (?, ?, ?)",
            (chat_id, rating, comment)
        )
        conn.commit()
        conn.close()
    
    def get_stats(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM chat_history")
        total_chats = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(rating) FROM feedback WHERE rating IS NOT NULL")
        avg_rating = cursor.fetchone()[0] or 0
        
        conn.close()
        return {"total_chats": total_chats, "avg_rating": round(avg_rating, 2)}