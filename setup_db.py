import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Books table
cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity INTEGER NOT NULL
)
""")

# Borrowed books table
cursor.execute("""
CREATE TABLE IF NOT EXISTS borrowed (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    student_name TEXT NOT NULL,
    student_id TEXT NOT NULL,
    borrow_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    FOREIGN KEY(book_id) REFERENCES books(id)
)
""")

# Insert 20 sample books
books = [
    ("Harry Potter 1", "J.K. Rowling", "Fantasy", 5),
    ("Harry Potter 2", "J.K. Rowling", "Fantasy", 5),
    ("Lord of the Rings 1", "Tolkien", "Fantasy", 3),
    ("Lord of the Rings 2", "Tolkien", "Fantasy", 4),
    ("Python Programming", "John Doe", "Education", 10),
    ("Flask Web Dev", "Miguel Grinberg", "Education", 8),
    ("React Basics", "Jane Smith", "Education", 7),
    ("Algorithms", "Cormen", "Education", 6),
    ("Data Structures", "Sedgewick", "Education", 5),
    ("Chemistry 101", "Albert", "Science", 3),
    ("Physics 101", "Newton", "Science", 4),
    ("Biology Basics", "Darwin", "Science", 5),
    ("Math for Everyone", "Euler", "Education", 10),
    ("English Literature", "Shakespeare", "Arts", 6),
    ("Art of War", "Sun Tzu", "History", 2),
    ("World History", "Herodotus", "History", 3),
    ("Geography Today", "Atlas", "Education", 4),
    ("Cooking 101", "Jamie Oliver", "Lifestyle", 5),
    ("Photography", "Ansel Adams", "Arts", 3),
    ("Meditation", "Buddha", "Lifestyle", 2)
]

cursor.executemany("INSERT INTO books (title, author, category, quantity) VALUES (?, ?, ?, ?)", books)
conn.commit()
conn.close()
print("Database setup complete!")
