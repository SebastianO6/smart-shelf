from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime, timedelta
import math

app = Flask(__name__)
app.secret_key = "smart_shelf_secure_key"

DATABASE = "database.db"
ADMIN_PASSWORD = "admin123"


# ---------------- DATABASE CONNECTION ----------------
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =====================================================
# PUBLIC HOME PAGE
# =====================================================
@app.route("/")
def home():
    search = request.args.get("search", "")

    conn = get_db()
    books = conn.execute(
        """SELECT * FROM books
           WHERE title LIKE ? OR author LIKE ?
           ORDER BY id DESC""",
        (f"%{search}%", f"%{search}%")
    ).fetchall()
    conn.close()

    return render_template("home.html", books=books, search=search)


# =====================================================
# ADMIN LOGIN
# =====================================================
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    error = None

    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin")
        else:
            error = "Invalid password"

    return render_template("admin_login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# =====================================================
# ADMIN DASHBOARD (BOOKS ONLY)
# =====================================================
@app.route("/admin")
def admin_dashboard():
    if not session.get("admin"):
        return redirect("/admin-login")

    search = request.args.get("search", "")

    conn = get_db()
    books = conn.execute(
        """SELECT * FROM books
           WHERE title LIKE ? OR author LIKE ?
           ORDER BY id DESC""",
        (f"%{search}%", f"%{search}%")
    ).fetchall()
    conn.close()

    return render_template("admin_dashboard.html",
                           books=books,
                           search=search)


# =====================================================
# ADD BOOK
# =====================================================
@app.route("/add", methods=["GET", "POST"])
def add_book():
    if not session.get("admin"):
        return redirect("/admin-login")

    if request.method == "POST":
        conn = get_db()
        conn.execute(
            "INSERT INTO books (title, author, category, quantity) VALUES (?, ?, ?, ?)",
            (request.form["title"],
             request.form["author"],
             request.form["category"],
             int(request.form["quantity"]))
        )
        conn.commit()
        conn.close()
        return redirect("/admin")

    return render_template("book_form.html", book=None)


# =====================================================
# EDIT BOOK
# =====================================================
@app.route("/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    if not session.get("admin"):
        return redirect("/admin-login")

    conn = get_db()
    book = conn.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()

    if request.method == "POST":
        conn.execute(
            """UPDATE books
               SET title=?, author=?, category=?, quantity=?
               WHERE id=?""",
            (request.form["title"],
             request.form["author"],
             request.form["category"],
             int(request.form["quantity"]),
             book_id)
        )
        conn.commit()
        conn.close()
        return redirect("/admin")

    conn.close()
    return render_template("book_form.html", book=book)


# =====================================================
# DELETE BOOK
# =====================================================
@app.route("/delete/<int:book_id>")
def delete_book(book_id):
    if not session.get("admin"):
        return redirect("/admin-login")

    conn = get_db()
    conn.execute("DELETE FROM books WHERE id=?", (book_id,))
    conn.commit()
    conn.close()

    return redirect("/admin")


# =====================================================
# BORROW BOOK
# =====================================================
@app.route("/borrow/<int:book_id>", methods=["GET", "POST"])
def borrow_book(book_id):
    if not session.get("admin"):
        return redirect("/admin-login")

    conn = get_db()
    book = conn.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()

    if request.method == "POST" and book and book["quantity"] > 0:
        borrow_date = datetime.now()
        due_date = borrow_date + timedelta(days=7)

        conn.execute(
            """INSERT INTO borrowed
               (book_id, student_name, student_id, borrow_date, due_date)
               VALUES (?, ?, ?, ?, ?)""",
            (book_id,
             request.form["student_name"],
             request.form["student_id"],
             borrow_date.strftime("%Y-%m-%d"),
             due_date.strftime("%Y-%m-%d"))
        )

        conn.execute(
            "UPDATE books SET quantity = quantity - 1 WHERE id=?",
            (book_id,)
        )

        conn.commit()
        conn.close()
        return redirect("/admin")

    conn.close()
    return render_template("borrow_form.html", book=book)


# =====================================================
# RETURN BOOK
# =====================================================
@app.route("/return/<int:borrow_id>")
def return_book(borrow_id):
    if not session.get("admin"):
        return redirect("/admin-login")

    conn = get_db()
    record = conn.execute(
        "SELECT * FROM borrowed WHERE id=?",
        (borrow_id,)
    ).fetchone()

    if record:
        conn.execute(
            "UPDATE books SET quantity = quantity + 1 WHERE id=?",
            (record["book_id"],)
        )
        conn.execute(
            "DELETE FROM borrowed WHERE id=?",
            (borrow_id,)
        )
        conn.commit()

    conn.close()
    return redirect("/borrowed")


# =====================================================
# BORROWED BOOKS PAGE (SEPARATE PAGE)
# =====================================================
@app.route("/borrowed")
def borrowed_list():
    if not session.get("admin"):
        return redirect("/admin-login")

    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")

    per_page = 10
    offset = (page - 1) * per_page

    conn = get_db()

    records = conn.execute("""
        SELECT borrowed.*, books.title
        FROM borrowed
        JOIN books ON borrowed.book_id = books.id
        WHERE student_name LIKE ?
           OR student_id LIKE ?
           OR books.title LIKE ?
        ORDER BY due_date ASC
        LIMIT ? OFFSET ?
    """, (f"%{search}%", f"%{search}%", f"%{search}%", per_page, offset)).fetchall()

    total = conn.execute("""
        SELECT COUNT(*)
        FROM borrowed
        JOIN books ON borrowed.book_id = books.id
        WHERE student_name LIKE ?
           OR student_id LIKE ?
           OR books.title LIKE ?
    """, (f"%{search}%", f"%{search}%", f"%{search}%")).fetchone()[0]

    conn.close()

    total_pages = math.ceil(total / per_page) if total else 1
    today = datetime.now().date().strftime("%Y-%m-%d")

    return render_template("borrowed_list.html",
                           records=records,
                           today=today,
                           page=page,
                           total_pages=total_pages,
                           search=search)


if __name__ == "__main__":
    app.run()
