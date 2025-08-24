import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_very_secret_key_change_me'

# --- Supabase API Configuration ---
# We get these from your .env file
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# This is the endpoint for your 'posts' table
API_ENDPOINT = f"{SUPABASE_URL}/rest/v1/posts"

# --- Helper function for headers ---
# Every request to Supabase needs these headers
def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

# Main route to display all posts
@app.route('/')
def index():
    # ?select=* orders by created_at descending
    params = {"select": "*", "order": "created_at.desc"}
    res = requests.get(API_ENDPOINT, headers=get_headers(), params=params)
    posts = res.json() if res.ok else []
    return render_template('index.html', posts=posts)

# Route to view a single post
@app.route('/post/<int:post_id>')
def post(post_id):
    # ?select=* and filter where id equals post_id
    params = {"select": "*", "id": f"eq.{post_id}"}
    res = requests.get(API_ENDPOINT, headers=get_headers(), params=params)
    # The result is a list, so we get the first item
    post_data = res.json()[0] if res.ok and res.json() else None
    return render_template('post.html', post=post_data)

# Route to create a new post
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title:
            flash('Title is required!')
        else:
            # The data we want to insert
            payload = {'title': title, 'content': content}
            requests.post(API_ENDPOINT, headers=get_headers(), json=payload)
            return redirect(url_for('index'))
    return render_template('create.html')

# Route to edit an existing post
@app.route('/edit/<int:post_id>', methods=('GET', 'POST'))
def edit(post_id):
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title:
            flash('Title is required!')
        else:
            # The data we want to update
            payload = {'title': title, 'content': content}
            # Filter to the specific post we want to update
            params = {"id": f"eq.{post_id}"}
            requests.patch(API_ENDPOINT, headers=get_headers(), json=payload, params=params)
            return redirect(url_for('index'))

    # GET request: Fetch the post data to pre-fill the form
    params = {"select": "*", "id": f"eq.{post_id}"}
    res = requests.get(API_ENDPOINT, headers=get_headers(), params=params)
    post_data = res.json()[0] if res.ok and res.json() else None
    return render_template('edit.html', post=post_data)

# Route to delete a post
@app.route('/delete/<int:post_id>', methods=('POST',))
def delete(post_id):
    # Filter to the specific post we want to delete
    params = {"id": f"eq.{post_id}"}
    requests.delete(API_ENDPOINT, headers=get_headers(), params=params)
    flash('Post was successfully deleted!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
