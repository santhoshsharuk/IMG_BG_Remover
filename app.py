from flask import Flask, render_template, request, send_file, redirect, url_for, abort
import os
from rembg import remove
from PIL import Image
import threading

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB file size limit

# Ensure uploads folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Function to delete files after a delay
def delete_files(*file_paths):
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted {file_path}")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Handle file upload
        if "file" not in request.files:
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            return redirect(request.url)
        if file:
            # Save the uploaded file
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # Remove background
            output_filename = "output.png"
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            with Image.open(filepath) as img:
                output = remove(img)
                output.save(output_path)

            # Schedule deletion of uploaded and processed images after 1 minute
            threading.Timer(60, delete_files, args=[filepath, output_path]).start()

            return render_template("index.html", result_image=output_filename)

    return render_template("index.html")

@app.route("/download")
def download():
    try:
        # Attempt to send the file
        return send_file("static/uploads/output.png", as_attachment=True)
    except FileNotFoundError:
        # If the file is not found, render the custom error page
        return render_template("file_not_found.html"), 404

# Custom 404 Error Handler
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

# Custom 500 Error Handler (Optional)
@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html"), 500

if __name__ == "__main__":
    app.run(debug=True)