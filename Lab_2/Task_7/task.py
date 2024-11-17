from app import app, db

# Push the app context explicitly
with app.app_context():
    db.create_all()
