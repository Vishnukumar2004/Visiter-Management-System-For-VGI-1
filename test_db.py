from models import connect_db, Visitor
import os

try:
    connect_db()
    count = Visitor.objects.count()
    print(f"Successfully connected to MongoDB!")
    print(f"Total visitors in database: {count}")
    
    if count > 0:
        first_visitor = Visitor.objects.first()
        print(f"First visitor in DB: {first_visitor.student_name}")
except Exception as e:
    print(f"Connection failed: {e}")
