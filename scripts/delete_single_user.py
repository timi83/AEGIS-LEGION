
import sys
from sqlalchemy import create_engine, text

def delete_user():
    print("--- DELETE SINGLE USER ---")
    
    db_url = input("Enter External Database URL: ").strip()
    if not db_url.startswith("postgres"):
        print("❌ Invalid URL")
        return
        
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    target_email = input("Enter email to delete: ").strip()
    if not target_email:
        print("❌ Email required.")
        return

    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            # 1. Find User ID
            result = conn.execute(text("SELECT id, username FROM users WHERE email = :email"), {"email": target_email})
            user = result.fetchone()
            
            if not user:
                print(f"❌ User with email '{target_email}' not found.")
                return
            
            user_id, username = user
            print(f"⚠️ Found User: {username} (ID: {user_id})")
            confirm = input(f"Type 'DELETE' to confirm deletion of {target_email}: ").strip()
            
            if confirm != "DELETE":
                print("Aborted.")
                return
            
            # 2. Delete Dependencies
            print("Cleaning Incident Assignments (for User's Incidents)...")
            # We must find the incidents belonging to this user first to delete their assignments?
            # Or simplified: delete ALL assignments where the incident belongs to this user.
            conn.execute(text("""
                DELETE FROM incident_assignments 
                WHERE incident_id IN (SELECT id FROM incidents WHERE user_id = :uid)
            """), {"uid": user_id})

            print("Cleaning Incident Notes...")
            conn.execute(text("""
                DELETE FROM incident_notes 
                WHERE incident_id IN (SELECT id FROM incidents WHERE user_id = :uid)
            """), {"uid": user_id})

            print("Cleaning Incidents...")
            conn.execute(text("DELETE FROM incidents WHERE user_id = :uid"), {"uid": user_id})
            
            print("Cleaning Audit Logs...")
            conn.execute(text("DELETE FROM audit_logs WHERE user_id = :uid"), {"uid": user_id})
            
            print("Cleaning Server Assignments...")
            conn.execute(text("DELETE FROM server_assignments WHERE user_id = :uid"), {"uid": user_id})
            
            # 3. Delete User
            print("Deleting User...")
            conn.execute(text("DELETE FROM users WHERE id = :uid"), {"uid": user_id})
            
            conn.commit()
            print(f"✅ User {target_email} has been deleted.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    delete_user()
