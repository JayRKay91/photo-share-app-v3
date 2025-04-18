# 📸 Photo Share App – Version 3

This is version 3 of the **Photo Share App**, a lightweight Flask-based media sharing platform designed for private image and video hosting. This version builds upon version 2 with cleaner code, improved organization, and new usability features.

---

## ✅ Features So Far

- 📁 **Albums Support**: Users can group media into albums using a dropdown menu. Albums are stored and managed via a JSON-based system.
- 🏷️ **Tags System**: Each photo/video can have one or more tags. A tag sidebar and search function allow users to filter the gallery.
- 🔍 **Search Bar**: The search bar can search across:
  - Tags
  - Descriptions
  - Filenames
- 📌 **Sticky Search Bar**: The search bar remains fixed at the top of the page while scrolling for easier navigation.
- 🧹 **Cleaner Code Refactor**: Updated project structure and code using insights from the `04-mini-high` model to improve logic, readability, and performance.
- 🖼️ **Image + Video Gallery**: Uploads support popular image formats (`.jpg`, `.png`, `.webp`, `.heic`, etc.) and videos (`.mp4`, `.mov`, `.avi`, etc.).
- 🎞️ **Thumbnails**: Automatically generated thumbnails for both images and videos.
- 💬 **Comments + Descriptions**: Each media item supports optional text fields and user-added comments.

---

## 📂 Project Structure

photo-share-app-v3/ ├── app/ │ ├── static/ │ ├── templates/ │ ├── init.py │ └── ... (route and helper modules) ├── run.py ├── requirements.txt └── README.md

yaml
Copy
Edit

---

## 🛠 Tech Stack

- **Flask** (Python)
- **HTML5 + CSS3**
- **MoviePy** (video thumbnails)
- **Pillow / pillow-heif** (image support incl. HEIC)
- **Gunicorn** (for production server, e.g., Render deployment)

---

## 🚀 Deployment

Currently deployed on [Render](https://render.com), using:
```bash
gunicorn run:app
🧪 Next Steps / In Progress
 Lightbox-style view for enlarging images/videos

 Audio/voice note attachments

 Image download button

 Folder-like album navigation

 Tag rename/edit/delete tools

vbnet
Copy
Edit

---

Would you like me to:
1. Write the terminal commands to add and push this file to GitHub?
2. Add a “version history” section with v1 and v2 summaries too?
3. Convert it to HTML or reStructuredText format for fancier documentation?

Let me know what else you'd like to include!