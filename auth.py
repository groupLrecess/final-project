from io import BytesIO
from flask import Blueprint, render_template, request, redirect,url_for, flash, current_app, jsonify, send_from_directory, send_file
from werkzeug.utils import secure_filename
import os
from flask_bcrypt import bcrypt
from . import db
from .models import Job , Company ,User, Resume, Upload
from .forms import RegistrationForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user,current_user
import smtplib
from email.message import EmailMessage


auth = Blueprint('auth', __name__)

external_jobs = [
    {'title': 'Marketing Manager', 'description': 'Promote the  company brand and services and optimizing our marketing strategies, managing the marketing department budget and staff, as well as preparing forecasts.', 'category': 'Marketing', 'location': 'Mbarara, Uganda', 'time': 'Full Time'},
    {'title': 'Product Designer', 'description': 'In charge of the entire product creation process. They are ultimately responsible for discovering and defining a problem, and then empathically designing a solution. ', 'category': 'Design & Creative', 'location': 'Kampala, Uganda', 'time': 'Full Time'},
    
    {'title': 'Creative Director', 'description': '', 'category': 'Business Development', 'location': 'Mbale, Uganda', 'time': 'Full Time'},
    
    {'title': 'Word Press Developer', 'description': 'Responsible for Developing core WordPress code that meets customer needs, designing and building custom WordPress plugins for third party services that integrate with Wordpress.', 'category': 'Customer Service', 'location': 'Gulu, Uganda', 'time': 'Part Time'},
    
    {'title': 'Project Manager', 'description': 'Accountable for planning and allocating resources, preparing budgets, monitoring progress, and keeping stakeholders informed throughout the project lifecycle.', 'category': 'Project Management', 'location': 'Kampala, Uganda', 'time': 'Part Time'},
    
    {'title': 'Sales Person', 'description': 'Sells products or services for a company and represents their brand. ', 'category': 'Sales & Communication', 'location': 'Kampala, Uganda', 'time': 'Part Time'},
    
    {'title': 'Kindergarten Teacher', 'description': 'Designing a teaching plan and using activities and instructional methods to motivate children.', 'category': 'Teaching & Education', 'location': 'Mbarara, Uganda', 'time': 'Part Time'},
    
    {'title': 'IT Specialist', 'description': 'Responsible for providing various forms of computer-related technical assistance and improving the efficiency of the work of the staff through the use of technology.', 'category': 'Customer Service', 'location': 'Kampala, Uganda', 'time': 'Internship'},
    
    {'title': 'Auditor', 'description': 'Reviews the accounting records, operational data, and financial records of companies to ensure their financial records are accurate and in line with generally accepted accounting principles.', 'category': 'Business Development', 'location': 'Gulu, Uganda', 'time': 'Internship'},
    
    {'title': 'Choreographer', 'description':'Designs and directs the dance or stylized movement in musical productions, working closely with the director and musical director.', 'category': 'Teaching & Education', 'location': 'Kampala, Uganda', 'time': 'Internship'},
    {'title': '3D Animator', 'description':'Designs realistic, three-dimensional animations for movies, television shows, and video games.', 'category': 'Design & Creative', 'location': 'Kampala, Uganda', 'time': 'Internship'},
]

# Home page - display job listings
@auth.route('/index')
def index():
    return render_template("index.html")


@auth.route('/search')
def search():
    keyword = request.form.get('keyword')
    category = request.form.get('category')
    location = request.form.get('location')

    # Query the database based on search parameters
    db_jobs = Job.query.filter(
        Job.title.ilike(f'%{keyword}%'),
        Job.category == category,
        Job.location == location
    ).all()

    filtered_external_jobs = [job for job in external_jobs
                              if (not keyword or keyword.lower() in job['title'].lower()) and
                                 (not category or category == job['category']) and
                                 (not location or location.lower() in job['location'].lower())]

    combined_jobs = db_jobs + filtered_external_jobs



    return render_template('search_results.html', jobs=combined_jobs)


@auth.route('/register_company', methods=['GET', 'POST'])
def register_company():
    if request.method == 'POST':
        # Access form data using request.form
        company_name = request.form['company_name']
        full_name = request.form['full_name']
        phone_number = request.form['phone_number']
        company = Company.query.filter_by(phone_number=phone_number).first()
        if company:
            return jsonify({'message': 'Company with the provided phone number already exists.'})
        
        new_company = Company(company_name=company_name, full_name=full_name, phone_number=phone_number)
        db.session.add(new_company)
        db.session.commit()
        return redirect(url_for("auth.post_job"))
        return {'message': 'company created success'}
    return {'message': 'failed'}



@auth.route('/company_list')
def company_list():
    companies = Company.query.all()
    company_list = []
    for company in companies:
        company_data = {
            'id': company.id,
            'full_name': company.full_name,
            'phone_number': company.phone_number
        }
        company_list.append(company_data)

    return jsonify({'companies': company_list})


@auth.route('/user_list')
def user_list():
    users = User.query.all()
    user_list = []
    for user in users:
        user_data = {
            'id': user.id,
            'email': user.email,
            'role': user.role
        }
        user_list.append(user_data)

    return jsonify({'users': user_list})

@auth.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        # Access form data using request.form
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        user = User.query.filter_by(email=email).first()
        if user:
            error_message = "User with the provided email already exists!"
            return render_template("register_user.html", error_message = error_message)
        
        new_user = User(name=name, email=email, password = generate_password_hash(password), role=role)
        db.session.add(new_user)
        db.session.commit()
        success_message = "Person registered successfully!"
        return redirect(url_for('auth.index'))
    return render_template("register_user.html")


@auth.route('/', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        # Access form data using request.form
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            error_message = "No user account!"
            return render_template("login_user.html", error_message = error_message)
        
        if user and user.check_password(password):
            success_message = "Login success!"
            # login_user(user)
            return redirect(url_for('auth.index', success_message = success_message))
        else: 
            error_message = "Wrong password!"
            return render_template("login_user.html", error_message = error_message)
          
    return render_template("login_user.html")



@auth.route('/post_job', methods=[ 'GET','POST'])
def post_job():
 if request.method == 'POST':
    
    title = request.form.get('title')
    description = request.form.get('description')
    category = request.form.get('category')  # Make sure this field is present in the form
    location = request.form.get('location')
    time = request.form.get('time')
    
    # Validate data and insert job into the database
    job = Job.query.filter_by(title=title).first()
    if job:
        new_job = Job(title=title, description=description, category=category, location=location, time=time)
        db.session.add(new_job)
        db.session.commit()
        flash('Job posted')
        return redirect(url_for('auth.joblist'))
 return render_template("post_job.html")

# Make sure you also have appropriate routes and templates for posting jobs

@auth.route('/joblist')
def job_listing():
    jobs = Job.query.all()
    return render_template('job-list.html', jobs=jobs)

@auth.route('/upload_resume', methods=['GET', 'POST'])
def upload_resume():
    if request.method == 'POST':
        file= request.files['resume']

        upload = Upload(filename=file.filename, data= file.read())
        db.session.add(upload)
        db.session.commit()

        return f'Uploaded: {file.filename}'
       
    return render_template('upload.html')


@auth.route('/create_resume', methods=['GET', 'POST'])
def create_resume():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        resume = request.files['resume']  # Access the uploaded resume file
        # Extract other form fields as needed

        # Save the uploaded resume file to the designated folder
        if resume:
            resume_filename = secure_filename(resume.filename)
            resume.save(os.path.join(current_app.config['UPLOAD_FOLDER'], resume.filename))

            # Process the resume data (optional: store in database)
            # For example, you could save the resume data to a database
            db.save_resume(name, email, resume_filename)  # Replace with actual database operation

            return 'Resume created successfully!'

    return render_template('create_resume.html')



@auth.route('/dashboard')
def dashboard():
        return render_template('student_dashboard.html')

@auth.route('/company')
def company():
        return render_template('company.html') 

  

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login_user'))


@auth.route('/review')
def resume():
    resumes = Resume.query.all()
    return render_template('review_resumes.html', resumes=resumes)


@auth.route('/serve_resume/<upload_id>', methods=['GET'])
def serve_resume(upload_id):
    upload = Upload.query.filter_by(id=upload_id).first()
    return send_file(BytesIO(upload.data), attachment_filename=upload.filename, as_attachment=True)



@auth.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        user_email = request.form.get('email')
        message = request.form.get('message')

        if not name or not user_email or not message:
            error_statement = "All fields are required."
            return render_template("contact.html", error_statement=error_statement)

        msg = EmailMessage()
        msg.set_content(message)

        msg['Subject'] = f'Message from {name}'
        msg['From'] = user_email
        msg['To'] = "kyavawarashidah5@gmail.com"  # Replace with your actual website email

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login("kyavawarashidah5@gmail.com", "irjwsmjvpimbfkwl")  # Replace with your Gmail email and password
                server.send_message(msg)
            
            success_message = "Message sent successfully!"
            return render_template("contact.html", success_message=success_message)
        except Exception as e:
            error_statement = f"An error occurred: {e}"
            return render_template("contact.html", error_statement=error_statement)

    return render_template("contact.html")







   

