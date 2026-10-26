
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session
from db import get_connection, get_library_connection
from functools import wraps
import bcrypt

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")



@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("library_page"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    errors = []
    name = ""
    email = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name:
            errors.append("Name is required")
        elif len(name) > 100:
            errors.append("Name is too long")

        if not email:
            errors.append("Email is required")
        elif len(email) > 255:
            errors.append("Email is too long")

        if not password:
            errors.append("Password is required")

        if not confirm_password:
            errors.append("Confirm password is required")

        if password and confirm_password and password != confirm_password:
            errors.append("Passwords do not match")

        if not errors:
            password_hash = bcrypt.hashpw(
                password.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            conn = None
            cursor = None

            try:
                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO users (email, name, password_hash)
                    VALUES (?, ?, ?)
                    """,
                    (email, name, password_hash)
                )

                conn.commit()

                cursor.execute(
                    "SELECT user_id FROM users WHERE email = ?",
                    (email,)
                )

                user = cursor.fetchone()

                if not user:
                    raise Exception("Unable to retrieve the registered user")

                session.clear()
                session["user_id"] = user[0]
                session["name"] = name

                return redirect(url_for("todos_page"))

            except Exception as e:
                if conn:
                    conn.rollback()

                error_message = " ".join(
                    str(arg) for arg in getattr(e, "args", ())
                ).lower()

                if (
                    "23000" in error_message
                    or "2627" in error_message
                    or "2601" in error_message
                    or "duplicate key" in error_message
                    or "unique constraint" in error_message
                ):
                    errors.append("Email Already Exists")
                else:
                    app.logger.exception("Registration failed")
                    errors.append(
                        "Registration failed. Please try again."
                    )

            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

    return render_template(
        "register.html",
        errors=errors,
        name=name,
        email=email
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    errors = []

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email:
            errors.append("Email is required")

        if not password:
            errors.append("Password is required")

        if not errors:
            conn = None
            cursor = None

            try:
                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT user_id, name, password_hash
                    FROM users
                    WHERE email = ?
                    """,
                    (email,)
                )

                user = cursor.fetchone()

                if user and bcrypt.checkpw(
                    password.encode("utf-8"),
                    user[2].encode("utf-8")
                ):
                    session.clear()
                    session["user_id"] = user[0]
                    session["name"] = user[1]

                    return redirect(url_for("library_page"))

                errors.append("Invalid email or password")

            except Exception:
                app.logger.exception("Login failed")
                errors.append("Login failed. Please try again.")

            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

    return render_template("login.html", errors=errors)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))

        return view(*args, **kwargs)

    return wrapped_view


def get_user_todos():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT todo_id, title, is_done, created_at
            FROM todos
            WHERE user_id = ?
            ORDER BY todo_id DESC
            """,
            (session["user_id"],)
        )

        rows = cursor.fetchall()

        return [
            {
                "todo_id": row[0],
                "title": row[1],
                "is_done": row[2],
                "created_at": row[3]
            }
            for row in rows
        ]

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def render_todos_with_errors(errors, status=200):
    todos = get_user_todos()
    open_count = sum(1 for todo in todos if not todo["is_done"])

    return render_template(
        "todos.html",
        todos=todos,
        name=session["name"],
        errors=errors,
        open_count=open_count
    ), status


@app.route("/todos")
@login_required
def todos_page():
    todos = get_user_todos()

    open_count = sum(
        1 for todo in todos
        if not todo["is_done"]
    )

    return render_template(
        "todos.html",
        todos=todos,
        name=session["name"],
        errors=[],
        open_count=open_count
    )


@app.route("/todos/add", methods=["POST"])
@login_required
def add_todo():
    title = request.form.get("title", "").strip()

    if not title:
        return render_todos_with_errors(["Title is required"], 400)

    if len(title) > 200:
        return render_todos_with_errors(["Title is too long"], 400)

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO todos (user_id, title)
            VALUES (?, ?)
            """,
            (session["user_id"], title)
        )

        conn.commit()

    except Exception:
        if conn:
            conn.rollback()

        app.logger.exception("Adding task failed")

        return render_todos_with_errors(
            ["Unable to add task. Please try again."],
            500
        )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for("todos_page"))


@app.route("/todos/<int:todo_id>/edit", methods=["POST"])
@login_required
def edit_todo(todo_id):
    title = request.form.get("title", "").strip()

    if not title:
        return render_todos_with_errors(["Title is required"], 400)

    if len(title) > 200:
        return render_todos_with_errors(["Title is too long"], 400)

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE todos
            SET title = ?
            WHERE todo_id = ? AND user_id = ?
            """,
            (title, todo_id, session["user_id"])
        )

        conn.commit()

    except Exception:
        if conn:
            conn.rollback()

        app.logger.exception("Updating task failed")

        return render_todos_with_errors(
            ["Unable to update task. Please try again."],
            500
        )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for("todos_page"))


@app.route("/todos/<int:todo_id>/toggle", methods=["POST"])
@login_required
def toggle_todo(todo_id):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE todos
            SET is_done = CASE
                WHEN is_done = 1 THEN 0
                ELSE 1
            END
            WHERE todo_id = ? AND user_id = ?
            """,
            (todo_id, session["user_id"])
        )

        conn.commit()

    except Exception:
        if conn:
            conn.rollback()

        app.logger.exception("Changing task status failed")

        return render_todos_with_errors(
            ["Unable to change task status. Please try again."],
            500
        )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for("todos_page"))


@app.route("/todos/<int:todo_id>/delete", methods=["POST"])
@login_required
def delete_todo(todo_id):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM todos
            WHERE todo_id = ? AND user_id = ?
            """,
            (todo_id, session["user_id"])
        )

        conn.commit()

    except Exception:
        if conn:
            conn.rollback()

        app.logger.exception("Deleting task failed")

        return render_todos_with_errors(
            ["Unable to delete task. Please try again."],
            500
        )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for("todos_page"))



@app.route("/library")
@login_required
def library_page():
    conn = None
    cursor = None

    try:
        conn = get_library_connection()
        cursor = conn.cursor()

        # Get all books
        cursor.execute("""
            SELECT book_id, title, price, author_id
            FROM book
            ORDER BY book_id DESC
        """)

        books = [
            {
                "book_id": row[0],
                "title": row[1],
                "price": row[2],
                "author_id": row[3]
            }
            for row in cursor.fetchall()
        ]

        # Get all authors
        cursor.execute("""
            SELECT author_id, name, country
            FROM author
            ORDER BY author_id
        """)

        authors = [
            {
                "author_id": row[0],
                "name": row[1],
                "country": row[2]
            }
            for row in cursor.fetchall()
        ]

        # Match each book with its author
        author_lookup = {
            author["author_id"]: author
            for author in authors
        }

        for book in books:
            author = author_lookup.get(book["author_id"])

            book["author_name"] = (
                author["name"] if author else "Unknown"
            )
            book["author_country"] = (
                author["country"] if author else "Unknown"
            )

        return render_template(
            "library.html",
            name=session["name"],
            books=books,
            authors=authors
        )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/library/authors/add", methods=["POST"])
@login_required
def add_author():
    name = request.form.get("name", "").strip()
    country = request.form.get("country", "").strip()

    if not name or not country:
        return redirect(url_for("library_page"))

    conn = None
    cursor = None

    try:
        conn = get_library_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO author (name, country) VALUES (?, ?)",
            (name, country)
        )
        conn.commit()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for("library_page"))


@app.route("/library/books/add", methods=["POST"])
@login_required
def add_book():
    title = request.form.get("title", "").strip()
    price_text = request.form.get("price", "").strip()
    author_id_text = request.form.get("author_id", "").strip()

    if not title or not price_text or not author_id_text:
        return redirect(url_for("library_page"))

    try:
        price = float(price_text)
        author_id = int(author_id_text)

        if price < 0:
            return redirect(url_for("library_page"))

    except ValueError:
        return redirect(url_for("library_page"))

    conn = None
    cursor = None

    try:
        conn = get_library_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT author_id FROM author WHERE author_id = ?",
            (author_id,)
        )

        if cursor.fetchone() is None:
            return redirect(url_for("library_page"))

        cursor.execute(
            """
            INSERT INTO book (title, price, author_id)
            VALUES (?, ?, ?)
            """,
            (title, price, author_id)
        )

        conn.commit()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for("library_page"))


@app.route("/library/books/<int:book_id>/edit", methods=["GET", "POST"])
@login_required
def edit_book(book_id):
    conn = None
    cursor = None

    try:
        conn = get_library_connection()
        cursor = conn.cursor()

        if request.method == "POST":
            title = request.form.get("title", "").strip()
            price_text = request.form.get("price", "").strip()
            author_id_text = request.form.get("author_id", "").strip()

            if not title or not price_text or not author_id_text:
                return redirect(url_for("library_page"))

            try:
                price = float(price_text)
                author_id = int(author_id_text)

                if price < 0:
                    return redirect(url_for("library_page"))

            except ValueError:
                return redirect(url_for("library_page"))

            cursor.execute(
                "SELECT author_id FROM author WHERE author_id = ?",
                (author_id,)
            )

            if cursor.fetchone() is None:
                return redirect(url_for("library_page"))

            cursor.execute(
                """
                UPDATE book
                SET title = ?, price = ?, author_id = ?
                WHERE book_id = ?
                """,
                (title, price, author_id, book_id)
            )

            conn.commit()
            return redirect(url_for("library_page"))

        cursor.execute(
            """
            SELECT book_id, title, price, author_id
            FROM book
            WHERE book_id = ?
            """,
            (book_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return redirect(url_for("library_page"))

        book = {
            "book_id": row[0],
            "title": row[1],
            "price": row[2],
            "author_id": row[3]
        }

        cursor.execute(
            "SELECT author_id, name FROM author ORDER BY name"
        )

        authors = [
            {"author_id": row[0], "name": row[1]}
            for row in cursor.fetchall()
        ]

        return render_template(
            "edit_book.html",
            name=session["name"],
            book=book,
            authors=authors
        )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/library/books/<int:book_id>/delete", methods=["POST"])
@login_required
def delete_book(book_id):
    conn = None
    cursor = None

    try:
        conn = get_library_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM book WHERE book_id = ?",
            (book_id,)
        )

        conn.commit()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for("library_page"))


@app.route("/library/authors/<int:author_id>/delete", methods=["POST"])
@login_required
def delete_author(author_id):
    conn = None
    cursor = None

    try:
        conn = get_library_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM author WHERE author_id = ?",
            (author_id,)
        )

        conn.commit()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for("library_page"))


@app.route("/library/authors/<int:author_id>/edit", methods=["GET", "POST"])
@login_required
def edit_author(author_id):
    conn = None
    cursor = None

    try:
        conn = get_library_connection()
        cursor = conn.cursor()

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            country = request.form.get("country", "").strip()

            if not name or not country:
                return redirect(url_for("library_page"))

            cursor.execute(
                """
                UPDATE author
                SET name = ?, country = ?
                WHERE author_id = ?
                """,
                (name, country, author_id)
            )

            conn.commit()
            return redirect(url_for("library_page"))

        cursor.execute(
            """
            SELECT author_id, name, country
            FROM author
            WHERE author_id = ?
            """,
            (author_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return redirect(url_for("library_page"))

        author = {
            "author_id": row[0],
            "name": row[1],
            "country": row[2]
        }

        return render_template(
            "edit_author.html",
            name=session["name"],
            author=author
        )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/logout", methods=["GET","POST"])
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
