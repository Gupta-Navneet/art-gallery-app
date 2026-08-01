# app.py - Online Art Gallery Application
import os
import io
import time
import sqlite3
import pandas as pd
import bcrypt
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

load_dotenv()

# -----------------------------
# Database Configuration & Manager
# -----------------------------
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "@Navneet gupta2106#")
DB_NAME = os.getenv("DB_NAME", "art_gallery")
DB_PORT = int(os.getenv("DB_PORT", "3306"))

class DatabaseManager:
    def __init__(self):
        self.db_type = None  # 'mysql' or 'sqlite'
        self.conn = None
        self.init_connection()

    def init_connection(self):
        if MYSQL_AVAILABLE:
            try:
                self.conn = mysql.connector.connect(
                    host=DB_HOST,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    database=DB_NAME,
                    port=DB_PORT,
                    connect_timeout=3
                )
                self.db_type = 'mysql'
                return
            except Exception:
                pass

        sqlite_db_path = os.path.join(os.path.dirname(__file__), "art_gallery.db")
        self.conn = sqlite3.connect(sqlite_db_path, check_same_thread=False)
        self.db_type = 'sqlite'

    def get_cursor(self):
        if self.db_type == 'mysql':
            try:
                if not self.conn.is_connected():
                    self.init_connection()
                return self.conn.cursor(dictionary=True, buffered=True)
            except Exception:
                self.init_connection()
                return self.conn.cursor(dictionary=True, buffered=True)
        else:
            return self.conn.cursor()

    def execute(self, query, params=()):
        cursor = self.get_cursor()
        if self.db_type == 'sqlite':
            adapted_query = query.replace("%s", "?")
            cursor.execute(adapted_query, params)
        else:
            cursor.execute(query, params)
        return cursor

    def commit(self):
        if self.conn:
            self.conn.commit()

    def fetchall(self, query, params=()):
        cursor = self.execute(query, params)
        rows = cursor.fetchall()
        if self.db_type == 'mysql':
            return [tuple(row.values()) for row in rows]
        return rows

    def fetchone(self, query, params=()):
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        if row and self.db_type == 'mysql':
            return tuple(row.values())
        return row

db = DatabaseManager()

# -----------------------------
# Table Setup & Full Data Seeding
# -----------------------------
def ensure_tables():
    if db.db_type == 'mysql':
        db.execute("""
            CREATE TABLE IF NOT EXISTS userss (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARBINARY(255) NOT NULL,
                role ENUM('admin', 'user') DEFAULT 'user'
            );
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS artists (
                id INT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                bio TEXT
            );
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS artworks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                artist_id INT,
                image_url VARCHAR(500),
                price DOUBLE,
                description TEXT,
                year INT,
                medium VARCHAR(100)
            );
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user VARCHAR(100),
                artwork_id INT,
                title VARCHAR(255),
                price DOUBLE,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INT AUTO_INCREMENT PRIMARY KEY,
                artwork_id INT,
                user VARCHAR(100),
                rating INT,
                comment TEXT,
                review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
    else:
        db.execute("""
            CREATE TABLE IF NOT EXISTS userss (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password BLOB NOT NULL,
                role TEXT DEFAULT 'user'
            );
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS artists (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                bio TEXT
            );
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS artworks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist_id INTEGER,
                image_url TEXT,
                price REAL,
                description TEXT,
                year INTEGER,
                medium TEXT
            );
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT,
                artwork_id INTEGER,
                title TEXT,
                price REAL,
                order_date DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artwork_id INTEGER,
                user TEXT,
                rating INTEGER,
                comment TEXT,
                review_date DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
    db.commit()
    seed_full_database()

def hash_pw(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def seed_full_database():
    """Populate database with complete real dataset if empty."""
    # Seed Artists
    existing_artists = db.fetchall("SELECT id FROM artists")
    if not existing_artists:
        artists_data = [
            (1, 'Leonardo da Vinci', 'Italian polymath of the Renaissance period.'),
            (2, 'Salvador Dalí', 'Spanish surrealist artist.'),
            (3, 'Edvard Munch', 'Norwegian painter and printmaker.'),
            (4, 'Pablo Picasso', 'Spanish painter, sculptor, and co-founder of Cubism.'),
            (5, 'Vincent van Gogh', 'Dutch post-impressionist painter, best known for works like "Starry Night" and "Sunflowers."'),
            (6, 'Claude Monet', 'French painter, one of the founders of French Impressionism, best known for "Water Lilies."'),
            (7, 'Frida Kahlo', 'Mexican painter, known for her deeply personal self-portraits and surrealist work.'),
            (8, 'Navneet Gupta', 'Indian Painter'),
            (9, 'goerge o kefee ', 'American modernist artist, famous for her paintings of enlarged flowers and New Mexico landscapes.'),
            (10, 'Grant Wood', 'American Painter'),
            (11, 'The girl with the pearl earing', 'Merican Painter')
        ]
        for a_id, name, bio in artists_data:
            try:
                db.execute("INSERT INTO artists (id, name, bio) VALUES (%s, %s, %s)", (a_id, name, bio))
            except Exception:
                pass
        db.commit()

    # Seed Artworks
    existing_artworks = db.fetchall("SELECT id FROM artworks")
    if not existing_artworks:
        artworks_data = [
            (19, 'The Persistence of Memory', 3, 'https://upload.wikimedia.org/wikipedia/en/d/dd/The_Persistence_of_Memory.jpg', 1300000.00, 'Iconic melting clocks painting by Salvador Dalí.', 1931, 'Oil on canvas'),
            (20, 'The Scream', 4, 'https://upload.wikimedia.org/wikipedia/commons/f/f4/The_Scream.jpg', 1100000.00, 'Expressionist masterpiece by Edvard Munch.', 1893, 'Oil, tempera, pastel'),
            (21, 'Guernica', 5, 'https://upload.wikimedia.org/wikipedia/en/7/74/PicassoGuernica.jpg', 1500000.00, 'Powerful anti-war mural by Pablo Picasso.', 1937, 'Oil on canvas'),
            (28, 'Starry Night', 1, 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/960px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg', 1500000.00, 'Famous painting by Vincent van Gogh.', 1889, 'Oil on canvas'),
            (29, 'Water Lilies', 2, 'https://www.artandobject.com/sites/default/files/styles/gallery_item/public/19331157-water-lilies0.jpg?h=7626f234&itok=WIZLL7rz', 1200000.00, 'Iconic series of paintings by Claude Monet.', 1916, 'Oil on canvas'),
            (30, 'The Two Fridas', 3, 'https://upload.wikimedia.org/wikipedia/en/f/f9/The_Two_Fridas.jpg', 2000000.00, 'Surrealist self-portrait by Frida Kahlo.', 1939, 'Oil on canvas'),
            (32, 'Mona Lisa', 1, 'https://upload.wikimedia.org/wikipedia/commons/6/6a/Mona_Lisa.jpg', 1000000.00, 'A portrait painting by Leonardo da Vinci.', 1503, 'Oil on canvas'),
            (37, 'Under the stars', 8, 'uploaded_images/20231018_204900.jpg', 5000000.00, 'A child stands under palm trees, gazing at the star-filled night sky.', 2020, 'Oil on canvas'),
            (39, 'Grant Wood', 10, 'uploaded_images/Grant_Wood_-_American_Gothic_-_Google_Art_Project.jpg', 3000000.00, 'The figures are seen as embodying positive aspects of rural American ideals, such as strength and stability', 1930, 'Oil of beaverboard')
        ]
        for aw_id, title, artist_id, img_url, price, desc, yr, med in artworks_data:
            try:
                db.execute(
                    "INSERT INTO artworks (id, title, artist_id, image_url, price, description, year, medium) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (aw_id, title, artist_id, img_url, price, desc, yr, med)
                )
            except Exception:
                pass
        db.commit()

    # Seed Users
    existing_users = db.fetchall("SELECT username FROM userss")
    if not existing_users:
        users_data = [
            ('Navneet Gupta', 'admin123', 'admin'),
            ('Navneet', 'navneet123', 'user'),
            ('admin', 'admin123', 'admin'),
            ('Nonu', 'nonu123', 'user'),
            ('Aditya', 'aditya123', 'user')
        ]
        for u, p, r in users_data:
            try:
                db.execute("INSERT INTO userss (username, password, role) VALUES (%s, %s, %s)", (u, hash_pw(p), r))
            except Exception:
                pass
        db.commit()

    # Seed Orders
    existing_orders = db.fetchall("SELECT id FROM orders")
    if not existing_orders:
        orders_data = [
            (1, 'Navneet', 19, 'The Persistence of Memory', 1300000.0, '2025-11-14 02:10:37'),
            (2, 'Aditya', 28, 'Starry Night', 1500000.0, '2025-11-14 02:47:14'),
            (3, 'Aditya', 37, 'Under the stars', 5000000.0, '2025-11-14 03:08:46'),
            (4, 'Aditya', 21, 'Guernica', 1500000.0, '2025-11-14 03:12:47'),
            (5, 'Navneet', 19, 'The Persistence of Memory', 1300000.0, '2025-11-14 10:50:18'),
            (6, 'Navneet', 39, 'Grant Wood', 3000000.0, '2025-11-14 11:02:28')
        ]
        for o_id, usr, aw_id, title, price, o_date in orders_data:
            try:
                db.execute("INSERT INTO orders (id, user, artwork_id, title, price, order_date) VALUES (%s, %s, %s, %s, %s, %s)",
                           (o_id, usr, aw_id, title, price, o_date))
            except Exception:
                pass
        db.commit()

    # Seed Reviews
    existing_reviews = db.fetchall("SELECT id FROM reviews")
    if not existing_reviews:
        reviews_data = [
            (1, 19, 'Navneet', 4, 'Stunning artwork!', '2025-11-14 02:17:42'),
            (2, 20, 'Aditya', 3, 'Great colors.', '2025-11-14 03:14:03'),
            (3, 21, 'Navneet', 5, 'Absolute masterpiece.', '2025-11-14 10:50:07'),
            (4, 29, 'Navneet', 5, 'Beautiful impressionist art.', '2025-11-14 11:02:07')
        ]
        for r_id, aw_id, usr, rating, comment, r_date in reviews_data:
            try:
                db.execute("INSERT INTO reviews (id, artwork_id, user, rating, comment, review_date) VALUES (%s, %s, %s, %s, %s, %s)",
                           (r_id, aw_id, usr, rating, comment, r_date))
            except Exception:
                pass
        db.commit()

ensure_tables()

# -----------------------------
# Helper Functions
# -----------------------------
def add_user(username, password, role):
    db.execute("INSERT INTO userss (username, password, role) VALUES (%s, %s, %s)",
               (username, hash_pw(password), role))
    db.commit()

def login_user(username, password, role):
    row = db.fetchone("SELECT password FROM userss WHERE username=%s AND role=%s", (username, role))
    if not row:
        return False
    stored = row[0]
    if isinstance(stored, str):
        stored = stored.encode('utf-8')
    try:
        return bcrypt.checkpw(password.encode('utf-8'), stored)
    except Exception:
        return False

def create_invoice_pdf_bytes(order_row):
    if not REPORTLAB_AVAILABLE:
        return None
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 50
    y = height - margin

    c.setFont("Helvetica-Bold", 20)
    c.drawString(margin, y, "ONLINE ART GALLERY - INVOICE")
    y -= 30

    c.setFont("Helvetica", 12)
    c.drawString(margin, y, f"Invoice ID: INV-{order_row[0]}")
    y -= 18
    c.drawString(margin, y, f"Customer: {order_row[1]}")
    y -= 18
    c.drawString(margin, y, f"Artwork: {order_row[3]}")
    y -= 18
    c.drawString(margin, y, f"Price: ₹{order_row[4]:,.2f}")
    y -= 18
    c.drawString(margin, y, f"Order Date: {order_row[5]}")
    y -= 30

    c.drawString(margin, y, "Thank you for supporting fine art!")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()

def create_invoice_text_bytes(order_row):
    lines = [
        "========================================",
        f"ONLINE ART GALLERY INVOICE - INV-{order_row[0]}",
        "========================================",
        f"Customer:   {order_row[1]}",
        f"Artwork:    {order_row[3]}",
        f"Price:      ₹{order_row[4]:,.2f}",
        f"Order Date: {order_row[5]}",
        "========================================",
        "Thank you for your purchase!"
    ]
    return "\n".join(lines).encode("utf-8")

# -----------------------------
# Streamlit Config & Session
# -----------------------------
st.set_page_config(
    page_title="🎨 Online Art Gallery",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎨 Online Art Gallery")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# -----------------------------
# Navigation Menu
# -----------------------------
def get_menu_options():
    if not st.session_state.logged_in:
        return ["Explore", "Login", "Sign Up"]

    if st.session_state.role == "admin":
        return [
            "View Artists",
            "Add Artist",
            "View Artworks",
            "Add Artwork",
            "Delete Artwork",
            "All Purchases"
        ]

    return [
        "View Artworks",
        "View Artists",
        "My Purchases"
    ]

menu = get_menu_options()
choice = st.sidebar.selectbox("Navigation Menu", menu)

if st.session_state.logged_in:
    st.sidebar.markdown(f"**Logged in as:** `{st.session_state.username}` ({st.session_state.role.upper()})")
    if st.sidebar.button("Logout", key="sidebar_logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()

# -----------------------------
# Artwork Grid Renderer
# -----------------------------
def render_artworks_grid(search_query="", show_reviews=True, tab_id="main"):
    if search_query:
        artworks = db.fetchall(
            "SELECT id, title, image_url, price, description, year, medium, artist_id FROM artworks WHERE title LIKE %s",
            ('%' + search_query + '%',)
        )
    else:
        artworks = db.fetchall(
            "SELECT id, title, image_url, price, description, year, medium, artist_id FROM artworks"
        )

    if not artworks:
        st.info("No artworks found matching your query.")
        return

    num_cols = 3
    cols = st.columns(num_cols)
    for idx, art in enumerate(artworks):
        art_id, title, image_url, price, description, year, medium, artist_id = art
        price = price or 0.0
        description = description or ""
        year = year or ""
        medium = medium or ""
        item_prefix = f"{tab_id}_art_{art_id}"

        with cols[idx % num_cols]:
            st.markdown(f"### {title}")
            if image_url:
                try:
                    # Clean aspect-ratio preserving display
                    st.image(image_url)
                except Exception:
                    st.text("🖼️ [Artwork Preview]")
            st.markdown(f"**Price:** ₹{price:,.2f}")
            st.markdown(f"**Year:** {year}  •  **Medium:** {medium}")
            st.markdown(f"_{description}_")

            show_buy = True
            if st.session_state.logged_in and st.session_state.role == "admin":
                show_buy = False

            buy_key = f"btn_buy_{item_prefix}"
            if show_buy:
                if st.button(f"🛒 Buy Now - {title}", key=buy_key):
                    if not st.session_state.logged_in:
                        st.warning("🔐 Please login as a user to purchase artworks!")
                    elif st.session_state.role == "admin":
                        st.error("❌ Admins cannot purchase artworks.")
                    else:
                        st.session_state.buy_modal = {
                            "art_id": art_id,
                            "title": title,
                            "price": price
                        }
            elif st.session_state.logged_in and st.session_state.role == "admin":
                st.info("Admins cannot purchase artworks.")

            if show_reviews:
                revs = db.fetchall(
                    "SELECT user, rating, comment, review_date FROM reviews WHERE artwork_id=%s ORDER BY review_date DESC",
                    (art_id,)
                )
                if revs:
                    st.markdown("**Reviews:**")
                    for r in revs:
                        user_name, rating, comment, rdate = r
                        stars = "⭐" * int(rating)
                        st.markdown(f"- **{user_name}** {stars} ({rating}/5)")
                        if comment:
                            st.caption(f"  \"{comment}\"")
                else:
                    st.caption("No reviews yet.")

            if st.session_state.logged_in:
                with st.expander("💬 Add a Review", expanded=False):
                    rate_key = f"rate_{item_prefix}"
                    comment_key = f"comment_{item_prefix}"
                    submit_key = f"submit_rev_{item_prefix}"
                    rating = st.slider("Rating (1-5)", 1, 5, 5, key=rate_key)
                    comment = st.text_area("Comment", key=comment_key)
                    if st.button("Submit Review", key=submit_key):
                        db.execute(
                            "INSERT INTO reviews (artwork_id, user, rating, comment) VALUES (%s, %s, %s, %s)",
                            (art_id, st.session_state.username, rating, comment)
                        )
                        db.commit()
                        st.success("✔ Review submitted!")
                        st.rerun()

    # Modal Purchase Dialog
    if "buy_modal" in st.session_state and st.session_state.buy_modal:
        modal_data = st.session_state.buy_modal
        with st.expander(f"🛒 Confirm Purchase: {modal_data['title']}", expanded=True):
            st.markdown(f"**Artwork:** {modal_data['title']}")
            st.markdown(f"**Price:** ₹{modal_data['price']:,.2f}")
            st.markdown(f"**Buyer:** {st.session_state.username}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirm Purchase", key="confirm_purchase"):
                    with st.spinner("Processing purchase..."):
                        time.sleep(0.6)
                        db.execute(
                            "INSERT INTO orders (user, artwork_id, title, price) VALUES (%s, %s, %s, %s)",
                            (st.session_state.username, modal_data['art_id'], modal_data['title'], modal_data['price'])
                        )
                        db.commit()
                        st.success(f"🎉 Payment successful! You purchased '{modal_data['title']}'")
                    st.session_state.buy_modal = None
                    st.rerun()

            with col2:
                if st.button("❌ Cancel", key="cancel_purchase"):
                    st.session_state.buy_modal = None
                    st.info("Purchase cancelled.")
                    st.rerun()

# -----------------------------
# Views: Public Explore
# -----------------------------
if choice == "Explore":
    st.header("🖼️ Public Art Gallery")
    q = st.text_input("🔍 Search Artwork by Title", key="explore_search")
    render_artworks_grid(search_query=q, show_reviews=True, tab_id="explore")

# -----------------------------
# Views: Sign Up
# -----------------------------
elif choice == "Sign Up":
    st.header("👤 Create Account")
    new_u = st.text_input("Username", key="su_username")
    new_p = st.text_input("Password", type="password", key="su_password")
    new_r = st.selectbox("Register as", ["user", "admin"], key="su_role")
    if st.button("Sign Up", key="su_btn"):
        if new_u and new_p:
            try:
                add_user(new_u, new_p, new_r)
                st.success(f"✅ {new_r.capitalize()} account created! Please log in.")
            except Exception as e:
                st.error("❗ Username already exists or invalid registration.")
        else:
            st.warning("Please fill out all fields.")

# -----------------------------
# Views: Login
# -----------------------------
elif choice == "Login":
    st.header("🔐 Login")
    li_u = st.text_input("Username", key="li_u")
    li_p = st.text_input("Password", type="password", key="li_p")
    li_r = st.selectbox("Login as", ["user", "admin"], key="li_r")
    if st.button("Login", key="li_btn"):
        if login_user(li_u, li_p, li_r):
            st.session_state.logged_in = True
            st.session_state.username = li_u
            st.session_state.role = li_r
            st.success(f"✅ Welcome back, {li_u}!")
            st.rerun()
        else:
            st.error("❌ Invalid credentials or role.")

# -----------------------------
# Views: Authenticated Features
# -----------------------------
if st.session_state.logged_in:
    role = st.session_state.role
    if role == "admin":
        tabs = ["View Artists", "Add Artist", "View Artworks", "Add Artwork", "Delete Artwork", "All Purchases"]
    else:
        tabs = ["View Artists", "View Artworks", "My Purchases"]

    tab_objs = st.tabs(tabs)

    # View Artists
    with tab_objs[0]:
        st.header("🧑‍🎨 Artists Directory")
        artists = db.fetchall("SELECT id, name, bio FROM artists")
        if artists:
            df = pd.DataFrame(artists, columns=["Artist ID", "Name", "Biography"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No artists registered yet.")

    # Add Artist (Admin)
    if role == "admin":
        with tab_objs[1]:
            st.header("➕ Add New Artist")
            a_id = st.number_input("Artist ID", min_value=1, step=1, key="a_id")
            a_name = st.text_input("Artist Name", key="a_name")
            a_bio = st.text_area("Biography", key="a_bio")
            if st.button("Save Artist", key="add_artist_btn"):
                if a_name:
                    db.execute("INSERT INTO artists (id, name, bio) VALUES (%s, %s, %s)", (a_id, a_name, a_bio))
                    db.commit()
                    st.success("✅ Artist added successfully.")
                else:
                    st.warning("Please enter artist name.")

    # View Artworks
    view_idx = tabs.index("View Artworks")
    with tab_objs[view_idx]:
        st.header("🖼️ Artwork Collection")
        q2 = st.text_input("Search Artworks", key="view_search")
        render_artworks_grid(search_query=q2, show_reviews=True, tab_id="viewtab")

    # Add Artwork (Admin)
    if role == "admin":
        with tab_objs[tabs.index("Add Artwork")]:
            st.header("➕ Add New Artwork")
            aw_title = st.text_input("Title", key="aw_title")
            aw_artist_id = st.number_input("Artist ID", min_value=1, key="aw_artist_id")
            aw_year = st.number_input("Year", min_value=0, max_value=2100, value=2024, key="aw_year")
            aw_medium = st.text_input("Medium (e.g. Oil on Canvas)", key="aw_medium")
            aw_price = st.number_input("Price (₹)", min_value=0.0, format="%.2f", key="aw_price")
            aw_desc = st.text_area("Description", key="aw_desc")
            aw_image = st.text_input("Image URL", key="aw_image")
            if st.button("Save Artwork", key="aw_submit"):
                if aw_title:
                    db.execute(
                        "INSERT INTO artworks (title, artist_id, image_url, price, description, year, medium) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                        (aw_title, aw_artist_id, aw_image, aw_price, aw_desc, aw_year, aw_medium)
                    )
                    db.commit()
                    st.success("✅ Artwork added successfully.")
                else:
                    st.warning("Please enter artwork title.")

    # Delete Artwork (Admin)
    if role == "admin":
        with tab_objs[tabs.index("Delete Artwork")]:
            st.header("❌ Delete Artwork")
            del_t = st.text_input("Title of Artwork to Delete", key="del_t")
            if st.button("Delete Artwork", key="del_btn"):
                if del_t:
                    db.execute("DELETE FROM artworks WHERE LOWER(title)=LOWER(%s)", (del_t,))
                    db.commit()
                    st.success(f"✅ Deleted artwork matching '{del_t}'.")
                else:
                    st.warning("Please specify title.")

    # All Purchases (Admin)
    if role == "admin":
        with tab_objs[tabs.index("All Purchases")]:
            st.header("📊 All Platform Purchases")
            all_orders = db.fetchall("SELECT id, user, artwork_id, title, price, order_date FROM orders ORDER BY order_date DESC")
            if all_orders:
                df_all = pd.DataFrame(all_orders, columns=["Order ID", "Customer Username", "Artwork ID", "Title", "Price (₹)", "Order Date"])
                st.dataframe(df_all, use_container_width=True)
            else:
                st.info("No purchases recorded yet.")

    # My Purchases (User)
    if role == "user":
        with tab_objs[tabs.index("My Purchases")]:
            st.header("📦 My Order History")
            my_orders = db.fetchall("SELECT id, user, artwork_id, title, price, order_date FROM orders WHERE user=%s ORDER BY order_date DESC", (st.session_state.username,))
            if not my_orders:
                st.info("You have not purchased any artworks yet.")
            else:
                df = pd.DataFrame(my_orders, columns=["Order ID", "Customer Username", "Artwork ID", "Title", "Price (₹)", "Order Date"])
                st.dataframe(df, use_container_width=True)

                opts = [f"INV-{o[0]} | {o[3]} | ₹{o[4]:,.2f}" for o in my_orders]
                sel = st.selectbox("Select order to download invoice:", opts, key="sel_inv")
                sel_idx = next(i for i, o in enumerate(my_orders) if f"INV-{o[0]}" in sel)
                order_row = my_orders[sel_idx]

                pdf_bytes = create_invoice_pdf_bytes(order_row)
                if pdf_bytes:
                    st.download_button(
                        "📄 Download Invoice (PDF)",
                        data=pdf_bytes,
                        file_name=f"invoice_INV-{order_row[0]}.pdf",
                        mime="application/pdf",
                        key=f"dl_pdf_{order_row[0]}"
                    )
                else:
                    txt_bytes = create_invoice_text_bytes(order_row)
                    st.download_button(
                        "📄 Download Invoice (TXT)",
                        data=txt_bytes,
                        file_name=f"invoice_INV-{order_row[0]}.txt",
                        mime="text/plain",
                        key=f"dl_txt_{order_row[0]}"
                    )

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown("<div style='text-align: center; color: #888;'>🎨 Online Art Gallery Platform  •  Built with Streamlit & Python</div>", unsafe_allow_html=True)
