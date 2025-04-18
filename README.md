# 📸 Photo Share App

A simple, private photo sharing web app built with Flask.  
Designed to be self-hosted on a Raspberry Pi or deployed via [Render](https://render.com).

---

## 🚀 Features

- Upload images via a web form
- View all uploaded images in a scrollable gallery
- Automatically creates upload directory if missing
- Responsive UI (mobile-friendly!)

---

## 🔧 Tech Stack

- **Backend:** Python, Flask
- **Server:** Gunicorn
- **Hosting:** Render (for testing), Raspberry Pi + NAS (for production)
- **Templates:** Jinja2
- **Storage:** Local filesystem (`/static/uploads`)

---

## 📁 Project Structure

photo-share-app/ ├── app/ │ ├── static/uploads/ # Uploaded images │ ├── templates/ # HTML templates │ ├── init.py # Flask app factory │ └── routes.py # Routes and upload logic ├── config.py # App configuration ├── requirements.txt # Python dependencies ├── render.yaml # Render deployment config ├── README.md # ← You're here! └── run.py # Entrypoint (optional)


---

## ⚙️ Deployment

### 🌐 Deploy to [Render](https://render.com)

1. Push your code to GitHub
2. Connect your repo to Render
3. Use the following settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn "app:create_app()"`
4. Done!

---

## 🛠 Local Setup

```bash
git clone https://github.com/JayRKay91/photo-share-app.git
cd photo-share-app
python -m venv venv
venv\Scripts\activate        # On Windows
pip install -r requirements.txt
python run.py                # Or manually run create_app()


💡 Future Ideas
User login system

Photo albums or tags

Image resizing / thumbnail generation

REST API support

Admin dashboard


---

### ✅ Add, Commit, and Push

Once saved, push to GitHub:

```bash
git add README.md
git commit -m "Add README file to document the project"
git push origin main
