# 🎨 Online Art Gallery Application

A full-featured **DBMS Art Gallery Management & E-Commerce Web Application** built with **Python**, **Streamlit**, and **MySQL / SQLite**.

---

## 🌐 Live Application
- **Live 24/7 Deployment**: [https://art-gallery-app-qwh4jcs7vrrdqrzwmyvpjy.streamlit.app/](https://art-gallery-app-qwh4jcs7vrrdqrzwmyvpjy.streamlit.app/)
- **GitHub Repository**: [https://github.com/Gupta-Navneet/art-gallery-app](https://github.com/Gupta-Navneet/art-gallery-app)

---

## 🗄️ Database Architecture & Schemas

The application is powered by a relational database model supporting both **MySQL** (for production database servers) and **SQLite** (for embedded/cloud deployment).

### 📊 Entity-Relationship (ER) Diagram

```mermaid
erdiagram
    USERSS {
        int id PK
        string username UK
        varbinary password
        enum role "admin | user"
    }

    ARTISTS {
        int id PK
        string name
        text bio
    }

    ARTWORKS {
        int id PK
        string title
        int artist_id FK
        string image_url
        double price
        text description
        int year
        string medium
    }

    ORDERS {
        int id PK
        string user
        int artwork_id FK
        string title
        double price
        timestamp order_date
    }

    REVIEWS {
        int id PK
        int artwork_id FK
        string user
        int rating
        text comment
        timestamp review_date
    }

    ARTISTS ||--o{ ARTWORKS : "creates"
    ARTWORKS ||--o{ ORDERS : "purchased in"
    ARTWORKS ||--o{ REVIEWS : "reviewed in"
    USERSS ||--o{ ORDERS : "places"
    USERSS ||--o{ REVIEWS : "writes"
```

---

### 📋 Table DDL Schemas

#### 1. `userss` Table
Stores registered users with role-based access control (`admin` vs `user`) and hashed passwords using `bcrypt`.
```sql
CREATE TABLE IF NOT EXISTS userss (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARBINARY(255) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user'
);
```

#### 2. `artists` Table
Stores artist profile details and biographies.
```sql
CREATE TABLE IF NOT EXISTS artists (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    bio TEXT
);
```

#### 3. `artworks` Table
Stores artwork inventory listings, pricing, medium, and image URLs linked to `artists`.
```sql
CREATE TABLE IF NOT EXISTS artworks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    artist_id INT,
    image_url VARCHAR(500),
    price DOUBLE,
    description TEXT,
    year INT,
    medium VARCHAR(100),
    FOREIGN KEY (artist_id) REFERENCES artists(id) ON DELETE SET NULL
);
```

#### 4. `orders` Table
Records customer transactions, order pricing, and purchase timestamps.
```sql
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user VARCHAR(100),
    artwork_id INT,
    title VARCHAR(255),
    price DOUBLE,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (artwork_id) REFERENCES artworks(id) ON DELETE SET NULL
);
```

#### 5. `reviews` Table
Stores customer ratings (1–5 stars) and feedback comments for artworks.
```sql
CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    artwork_id INT,
    user VARCHAR(100),
    rating INT,
    comment TEXT,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (artwork_id) REFERENCES artworks(id) ON DELETE CASCADE
);
```

---

## ⚡ SQL CRUD Operations

Below are the exact SQL queries executed by the application backend for each CRUD operation:

### 1. ➕ CREATE Operations (INSERT)

- **Create User Account**:
  ```sql
  INSERT INTO userss (username, password, role) 
  VALUES ('Navneet', '$2b$12$e8...', 'user');
  ```

- **Add New Artist (Admin)**:
  ```sql
  INSERT INTO artists (id, name, bio) 
  VALUES (8, 'Navneet Gupta', 'Indian Painter');
  ```

- **Add New Artwork (Admin)**:
  ```sql
  INSERT INTO artworks (title, artist_id, image_url, price, description, year, medium) 
  VALUES ('Under the stars', 8, 'uploaded_images/20231018_204900.jpg', 5000000.00, 'A child stands under palm trees, gazing at the star-filled night sky.', 2020, 'Oil on canvas');
  ```

- **Record Purchase Transaction**:
  ```sql
  INSERT INTO orders (user, artwork_id, title, price) 
  VALUES ('Aditya', 37, 'Under the stars', 5000000.00);
  ```

- **Submit Artwork Review**:
  ```sql
  INSERT INTO reviews (artwork_id, user, rating, comment) 
  VALUES (19, 'Navneet', 5, 'Stunning masterpiece with vivid details.');
  ```

---

### 2. 🔍 READ Operations (SELECT)

- **Public Gallery Search (by Title)**:
  ```sql
  SELECT id, title, image_url, price, description, year, medium, artist_id 
  FROM artworks 
  WHERE title LIKE '%Starry%';
  ```

- **User Authentication / Login Check**:
  ```sql
  SELECT password FROM userss 
  WHERE username = 'Navneet' AND role = 'user';
  ```

- **Fetch Artist Directory**:
  ```sql
  SELECT id, name, bio FROM artists;
  ```

- **Fetch Reviews for Specific Artwork**:
  ```sql
  SELECT user, rating, comment, review_date 
  FROM reviews 
  WHERE artwork_id = 19 
  ORDER BY review_date DESC;
  ```

- **Fetch Customer Order History**:
  ```sql
  SELECT id, user, artwork_id, title, price, order_date 
  FROM orders 
  WHERE user = 'Navneet' 
  ORDER BY order_date DESC;
  ```

- **Fetch Platform Purchases Analytics (Admin)**:
  ```sql
  SELECT id, user, artwork_id, title, price, order_date 
  FROM orders 
  ORDER BY order_date DESC;
  ```

---

### 3. ❌ DELETE Operations

- **Delete Artwork (Admin)**:
  ```sql
  DELETE FROM artworks 
  WHERE LOWER(title) = LOWER('Grant Wood');
  ```

---

## ✨ Application Features

- **Public Gallery & Search**: Search and view artwork collection without logging in.
- **User Authentication**: Secure signup and login powered by `bcrypt` password hashing.
- **Role-Based Control**:
  - **User**: Buy artworks, leave 1-5 star ratings & reviews, view purchase history, download PDF or TXT invoices.
  - **Admin**: Add new artists, add/delete artworks, view platform sales analytics.
- **Dual Database Architecture**: Automatically connects to a **MySQL** server if configured via environment variables, or falls back seamlessly to **SQLite** (`art_gallery.db`) for 24/7 cloud deployment.
- **PDF Invoice Generation**: Instant downloadable PDF invoices built with `ReportLab`.

---

## 💻 Local Setup & Execution

1. **Clone Repository**:
   ```bash
   git clone https://github.com/Gupta-Navneet/art-gallery-app.git
   cd art-gallery-app
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Application**:
   ```bash
   streamlit run app.py
   ```

4. **Access in Browser**: `http://localhost:8501`

---

## 🔐 Default Admin Account
- **Username**: `admin`
- **Password**: `admin123`
