# 🎨 Online Art Gallery Application

A full-featured Art Gallery Management & E-Commerce Web Application built with **Python**, **Streamlit**, and **MySQL / SQLite**.

---

## ✨ Features

- **Public Gallery**: Browse, search, and preview artworks and artists without logging in.
- **User Authentication**: Secure Sign-up and Login using `bcrypt` password hashing.
- **Role-Based Access Control**:
  - **User**: Purchase artworks with confirmation modal, leave ratings & reviews, view order history, download PDF or TXT invoices.
  - **Admin**: Manage Artists (View & Add), Manage Artworks (View, Add, Delete), View platform-wide purchase analytics.
- **Resilient Database Manager**: Automatically connects to **MySQL** if configured via environment variables, or falls back to an embedded **SQLite** database (`art_gallery.db`) for instant deployment anywhere.
- **PDF Invoice Generation**: Automatically generates downloadable PDF invoices using `ReportLab`.

---

## 🚀 Deployment Options

### Option 1: Streamlit Community Cloud (Recommended - 100% Free & Fastest)

Streamlit Community Cloud is the easiest way to host Streamlit applications directly from GitHub:

1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for Art Gallery app"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/art-gallery-app.git
   git push -u origin main
   ```
2. Go to **[share.streamlit.io](https://share.streamlit.io/)** and sign in with GitHub.
3. Click **"New app"**.
4. Select your repository (`art-gallery-app`), branch (`main`), and set Main file path to `app.py`.
5. *(Optional)* Expand **Advanced Settings** to set Environment Variables if connecting to an external MySQL server:
   - `DB_HOST`: Your MySQL host (e.g. Aiven, PlanetScale, CleverCloud)
   - `DB_USER`: Username
   - `DB_PASSWORD`: Password
   - `DB_NAME`: Database name
   - `DB_PORT`: 3306
6. Click **"Deploy!"**. Your app will be live on a public `.streamlit.app` URL within 1-2 minutes!

---

### Option 2: Deploy on Render

1. Push your code to GitHub.
2. Log in to **[Render.com](https://render.com/)**.
3. Click **New +** -> **Web Service**.
4. Connect your GitHub repository.
5. Set the settings:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
6. Click **Create Web Service**. Render will build and deploy your app automatically!

---

### Option 3: Deploy using Docker / Railway / Koyeb

If deploying with Docker:
```bash
docker build -t art-gallery-app .
docker run -p 8501:8501 art-gallery-app
```
Then access the app at `http://localhost:8501`.

---

## 💻 Running Locally

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Application**:
   ```bash
   streamlit run app.py
   ```

3. Open `http://localhost:8501` in your browser.

---

## 🔐 Default Admin Account
- **Username**: `admin`
- **Password**: `admin123`
*(You can also sign up for new User or Admin accounts directly from the Sign Up page).*
