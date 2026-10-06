from flask import Blueprint, request, render_template, redirect
from post_rules import validate_post
from repositories.posts import find_all, find_post, create_post, update_post, delete_post

posts_bp = Blueprint("posts", __name__)

@posts_bp.get("/")
def index():
    return render_template("index.html", posts=find_all())

@posts_bp.get("/board/<int:post_id>")
def detail(post_id):
    post = find_post(post_id)
    if post is None:
        return render_template("error.html", message="게시글을 찾을 수 없습니다."), 404
    return render_template("detail.html", post=post)

@posts_bp.route("/board/new", methods=["GET", "POST"])
def new():
    if request.method == "GET":
        return render_template("new.html", title="", body="", error=None)
    title = request.form.get("title", "").strip()
    body = request.form.get("body", "").strip()
    valid, error = validate_post(title, body)
    if not valid:
        return render_template("new.html", title=title, body=body, error=error), 400
    post = create_post(title, body)
    return redirect(f"/board/{post['id']}", code=303)

@posts_bp.route("/board/<int:post_id>/edit", methods=["GET", "POST"])
def edit(post_id):
    post = find_post(post_id)
    if post is None:
        return render_template("error.html", message="게시글을 찾을 수 없습니다."), 404
    if request.method == "GET":
        return render_template("edit.html", post=post, error=None)
    title = request.form.get("title", "").strip()
    body = request.form.get("body", "").strip()
    valid, error = validate_post(title, body)
    if not valid:
        return render_template("edit.html", post={"id": post_id, "title": title, "body": body}, error=error), 400
    updated = update_post(post_id, title, body)
    if updated is None:
        return render_template("error.html", message="게시글을 찾을 수 없습니다."), 404
    return redirect(f"/board/{post_id}", code=303)

@posts_bp.route("/board/<int:post_id>/delete", methods=["GET", "POST"])
def delete(post_id):
    post = find_post(post_id)
    if post is None:
        return render_template("error.html", message="게시글을 찾을 수 없습니다."), 404
    if request.method == "GET":
        return render_template("delete.html", post=post)
    deleted = delete_post(post_id)
    if deleted is None:
        return render_template("error.html", message="게시글을 찾을 수 없습니다."), 404
    return redirect("/", code=303)
