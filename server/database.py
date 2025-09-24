from flask_pymongo import PyMongo

mongo = PyMongo()

def initialize_db(app):
    try:
        print(f"Connecting to MongoDB with URI: {app.config['MONGO_URI'][:50]}...")
        mongo.init_app(app)
        
        # Test the connection
        with app.app_context():
            # Try to ping the database
            info = mongo.db.command("ping")
            print("✅ Database initialized and connected successfully!")
            print(f"Database name: {mongo.db.name}")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        print("Make sure MongoDB is running and the connection string is correct.")
