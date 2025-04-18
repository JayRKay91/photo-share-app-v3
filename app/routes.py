import os
import json
import uuid
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory, abort
from werkzeug.utils import secure_filename
from PIL import Image
import pillow_heif
from moviepy.video.io.VideoFileClip import VideoFileClip

main = Blueprint("main", __name__)

# —— Configuration Constants —— #
# These will pick up your app’s config at runtime
UPLOAD_FOLDER = None  # set in index() based on current_app.config
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR  # JSON files live here
DESCRIPTION_PATH = DATA_DIR / "descriptions.json"
ALBUM_PATH       = DATA_DIR / "albums.json"
COMMENTS_PATH    = DATA_DIR / "comments.json"
TAGS_PATH        = DATA_DIR / "tags.json"
THUMB_FOLDER     = BASE_DIR / "app" / "static" / "thumbnails"
THUMB_SIZE_WIDTH = 320

IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "webp", "heic"}
VIDEO_EXTENSIONS = {"mp4", "mov", "avi", "mkv"}
ALLOWED_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS

# ensure thumbnail dir exists
THUMB_FOLDER.mkdir(parents=True, exist_ok=True)


def allowed_file(filename: str) -> bool:
    """Check file extension against allowed list."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def load_json(path: Path) -> dict:
    """Load JSON from disk, return empty dict on missing or invalid."""
    if path.exists():
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError:
            current_app.logger.error(f"Invalid JSON in {path}")
    return {}


def save_json(path: Path, data: dict) -> None:
    """Pretty‑print JSON data back to disk."""
    path.write_text(json.dumps(data, indent=2))


def generate_video_thumbnail(video_path: Path, thumb_path: Path) -> None:
    """Grab a frame halfway through the video and save as JPEG thumbnail."""
    try:
        with VideoFileClip(str(video_path)) as clip:
            t = clip.duration / 2 if clip.duration > 1 else 0.1
            frame = clip.get_frame(t)
        img = Image.fromarray(frame)
        if img.mode != "RGB":
            img = img.convert("RGB")
        w, h = img.size
        new_h = int(h * (THUMB_SIZE_WIDTH / w))
        img = img.resize((THUMB_SIZE_WIDTH, new_h), Image.Resampling.LANCZOS)
        thumb_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(thumb_path), format="JPEG")
    except Exception as e:
        current_app.logger.error(f"Error generating thumbnail for {video_path}: {e}")
        raise


def sanitize_filename(filename: str) -> str:
    """Ensure incoming filename is a safe basename (no ../)."""
    clean = secure_filename(filename)
    if clean != filename:
        abort(400, "Invalid filename.")
    return filename


@main.route("/")
def index():
    """Gallery view, supports ?tag= and ?search= filters."""
    global UPLOAD_FOLDER
    UPLOAD_FOLDER = Path(current_app.config["UPLOAD_FOLDER"])
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    descs   = load_json(DESCRIPTION_PATH)
    albums  = load_json(ALBUM_PATH)
    comments= load_json(COMMENTS_PATH)
    tags    = load_json(TAGS_PATH)

    tag_filter    = request.args.get("tag", "").strip().lower()
    search_query  = request.args.get("search", "").strip().lower()

    # sort by modified time descending
    media_files = sorted(
        [f for f in UPLOAD_FOLDER.iterdir() if f.is_file()],
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    images = []
    for path in media_files:
        fn  = path.name
        ext = path.suffix.lstrip(".").lower()
        file_tags = tags.get(fn, [])
        lt = [t.lower() for t in file_tags]

        if tag_filter and tag_filter not in lt:
            continue
        if search_query:
            if not (
                search_query in fn.lower()
                or search_query in descs.get(fn, "").lower()
                or search_query in albums.get(fn, "").lower()
                or any(search_query in t.lower() for t in file_tags)
            ):
                continue

        media_type = "video" if ext in VIDEO_EXTENSIONS else "image"
        thumb = f"thumbnails/{path.stem}.jpg" if media_type == "video" else None

        images.append({
            "filename":    fn,
            "description": descs.get(fn, ""),
            "album":       albums.get(fn, ""),
            "comments":    comments.get(fn, []),
            "tags":        file_tags,
            "type":        media_type,
            "thumb":       thumb,
        })

    all_tags = sorted({t for lst in tags.values() for t in lst}, key=str.lower)

    return render_template(
        "gallery.html",
        images=images,
        descriptions=descs,
        albums=albums,
        tags=tags,
        all_tags=all_tags,
        current_tag=tag_filter,
        search_query=search_query
    )


@main.route("/upload", methods=["GET", "POST"])
def upload():
    """Upload handler: saves files, converts HEIC, generates thumbs."""
    if request.method == "POST":
        files = request.files.getlist("photos")
        album = request.form.get("album", "").strip()

        descs    = load_json(DESCRIPTION_PATH)
        albums   = load_json(ALBUM_PATH)
        comments = load_json(COMMENTS_PATH)
        tags     = load_json(TAGS_PATH)

        for file in files:
            if file and allowed_file(file.filename):
                orig = secure_filename(file.filename)
                ext  = orig.rsplit(".", 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                save_path = UPLOAD_FOLDER / filename

                # HEIC conversion
                if ext == "heic":
                    try:
                        hf = pillow_heif.read_heif(file.stream)
                        img = Image.frombytes(hf.mode, hf.size, hf.data, "raw")
                        filename = f"{uuid.uuid4().hex}.jpg"
                        save_path = UPLOAD_FOLDER / filename
                        img.save(str(save_path), format="JPEG")
                        flash("HEIC converted and uploaded.", "success")
                    except Exception as e:
                        flash(f"HEIC conversion failed: {e}", "error")
                        continue
                else:
                    file.save(str(save_path))

                # Thumbnail for videos
                if ext in VIDEO_EXTENSIONS:
                    thumb_file = THUMB_FOLDER / f"{save_path.stem}.jpg"
                    try:
                        generate_video_thumbnail(save_path, thumb_file)
                    except Exception as e:
                        flash(f"Thumbnail failed for {filename}: {e}", "error")

                if album:
                    albums[filename] = album
                descs[filename]    = ""
                comments[filename] = []
                tags[filename]     = []

        save_json(DESCRIPTION_PATH, descs)
        save_json(ALBUM_PATH, albums)
        save_json(COMMENTS_PATH, comments)
        save_json(TAGS_PATH, tags)

        flash("Upload successful.", "success")
        return redirect(url_for("main.index"))

    return render_template("upload.html")


@main.route("/add_tag/<filename>", methods=["POST"])
def add_tag(filename):
    """Add a single tag to one file."""
    fn = sanitize_filename(filename)
    tags = load_json(TAGS_PATH)
    new = request.form.get("tag", "").strip()
    if new:
        tags.setdefault(fn, [])
        if new not in tags[fn]:
            tags[fn].append(new)
            save_json(TAGS_PATH, tags)
            flash(f"Tag '{new}' added.", "success")
        else:
            flash(f"Tag '{new}' exists.", "info")
    else:
        flash("Empty tag not added.", "warning")
    return redirect(url_for("main.index"))


@main.route("/remove_tag/<filename>/<tag>", methods=["POST"])
def remove_tag(filename, tag):
    """Remove one tag from one file."""
    fn = sanitize_filename(filename)
    tags = load_json(TAGS_PATH)
    tags.setdefault(fn, [])
    tags[fn] = [t for t in tags[fn] if t.lower() != tag.lower()]
    save_json(TAGS_PATH, tags)
    flash(f"Tag '{tag}' removed.", "success")
    return redirect(url_for("main.index"))


@main.route("/rename_tag_single", methods=["POST"])
def rename_tag_single():
    """Rename a tag for a single file."""
    fn = sanitize_filename(request.form.get("filename", ""))
    old = request.form.get("old_tag", "").strip().lower()
    new = request.form.get("new_tag", "").strip()
    if not old or not new:
        flash("Missing rename data.", "warning")
        return redirect(url_for("main.index"))

    tags = load_json(TAGS_PATH)
    tags.setdefault(fn, [])
    tags[fn] = [new if t.lower() == old else t for t in tags[fn]]
    save_json(TAGS_PATH, tags)
    flash(f"Renamed '{old}'→'{new}' on {fn}.", "success")
    return redirect(url_for("main.index"))


@main.route("/rename_tag_global", methods=["POST"])
def rename_tag_global():
    """Rename a tag across all files."""
    old = request.form.get("old_tag", "").strip().lower()
    new = request.form.get("new_tag", "").strip()
    if not old or not new:
        flash("Missing rename data.", "warning")
        return redirect(url_for("main.index"))

    tags = load_json(TAGS_PATH)
    updated = False
    for fn, lst in tags.items():
        new_lst = [new if t.lower() == old else t for t in lst]
        if new_lst != lst:
            tags[fn] = new_lst
            updated = True

    if updated:
        save_json(TAGS_PATH, tags)
        flash(f"Renamed '{old}'→'{new}' globally.", "success")
    else:
        flash(f"No matches for '{old}'.", "info")
    return redirect(url_for("main.index"))


@main.route("/tag/<tagname>")
def filter_by_tag(tagname):
    """Quick redirect to apply tag filter."""
    return redirect(url_for("main.index", tag=tagname))


@main.route("/delete/<filename>", methods=["POST"])
def delete_image(filename):
    """Delete file, its thumbnail, and all metadata."""
    fn = sanitize_filename(filename)
    fp = UPLOAD_FOLDER / fn
    tp = THUMB_FOLDER / f"{Path(fn).stem}.jpg"

    descs    = load_json(DESCRIPTION_PATH)
    albums   = load_json(ALBUM_PATH)
    comments = load_json(COMMENTS_PATH)
    tags     = load_json(TAGS_PATH)

    if fp.exists():
        fp.unlink()
        descs.pop(fn, None)
        albums.pop(fn, None)
        comments.pop(fn, None)
        tags.pop(fn, None)
        if tp.exists():
            tp.unlink()
        flash(f"{fn} deleted.", "success")
    else:
        flash(f"{fn} not found.", "error")

    save_json(DESCRIPTION_PATH, descs)
    save_json(ALBUM_PATH, albums)
    save_json(COMMENTS_PATH, comments)
    save_json(TAGS_PATH, tags)
    return redirect(url_for("main.index"))


@main.route("/download/<filename>")
def download_image(filename):
    """Serve a file download."""
    fn = sanitize_filename(filename)
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], fn, as_attachment=True)


@main.route("/update_description/<filename>", methods=["POST"])
def update_description(filename):
    """Change the description text for one file."""
    fn = sanitize_filename(filename)
    descs = load_json(DESCRIPTION_PATH)
    descs[fn] = request.form.get("description", "").strip()
    save_json(DESCRIPTION_PATH, descs)
    flash("Description updated.", "success")
    return redirect(url_for("main.index"))


@main.route("/add_comment/<filename>", methods=["POST"])
def add_comment(filename):
    """Append a comment to one file."""
    fn = sanitize_filename(filename)
    comments = load_json(COMMENTS_PATH)
    c = request.form.get("comment", "").strip()
    if c:
        comments.setdefault(fn, []).append(c)
        save_json(COMMENTS_PATH, comments)
        flash("Comment added.", "success")
    else:
        flash("Empty comment not added.", "warning")
    return redirect(url_for("main.index"))
