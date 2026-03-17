import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from app.models import UserProfile
from app.forms import LoginForm, UploadForm


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")


@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)

        flash('File uploaded!', 'success')
        return redirect(url_for('upload'))
    elif request.method == 'POST':
        flash_errors(form)
    return render_template('upload.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():  # ensures username and password were entered
        username = form.username.data
        password = form.password.data

        # Query the database for the user
        user = UserProfile.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)  # logs the user in
            flash('You have successfully logged in!', 'success')
            return redirect(url_for('upload'))
        else:
            flash('Invalid username or password', 'danger')
    elif request.method == 'POST':
        flash_errors(form)

    return render_template('login.html', form=form)


# user_loader callback
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()


###
# Helper functions
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error in the {getattr(form, field).label.text} field - {error}", 'danger')


# Helper function to get list of uploaded images
def get_uploaded_images():
    uploaded_files = []
    upload_folder = app.config['UPLOAD_FOLDER']

    if not os.path.exists(upload_folder):
        return uploaded_files  # Return empty list if folder doesn't exist

    for file in os.listdir(upload_folder):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):  # Filter image files only
            uploaded_files.append(file)

    return uploaded_files


###
# Routes for uploaded files
###

# Route to serve uploaded images
@app.route('/uploads/<filename>')
@login_required
def get_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# Route to display list of uploaded images in a grid
@app.route('/files')
@login_required
def files():
    images = get_uploaded_images()
    return render_template('files.html', images=images)


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))


###
# Headers and error handlers
###

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404