from flask import Flask, render_template, send_from_directory

# In this example, we have a Flask application that serves static HTML files from the HTML_Files directory in the project.
# The HTML files are stored in the HTML_Files directory, and the Flask application is configured to serve these files using the send_from_directory function.
# The index route returns the index.html file, and the send_file route serves any static file from the HTML_Files directory based on the filename provided in the URL.
# This allows us to create a simple Flask application that serves static HTML files without the need to create routes for each individual file.
# To run the application, we can execute the app.py file and access the index.html file in the browser:
# $ python app.py
# The application will be running on a development server, and we can access the index.html file by visiting http:// http://127.0.0.1:5000/ in the browser.


app = Flask(__name__, static_folder='HTML_Files', template_folder='HTML_Files')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:filename>')
def send_file(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    app.run(debug=True)


