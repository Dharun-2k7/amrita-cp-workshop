from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Migrating Database...")
    try:
        db.session.execute(text('ALTER TABLE problem ADD COLUMN scheduled_for TIMESTAMP'))
        db.session.commit()
        print("Successfully added scheduled_for column to problem table.")
    except Exception as e:
        print(f"Migration failed or column already exists: {e}")
        db.session.rollback()
