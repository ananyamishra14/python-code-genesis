
"""
Database models for the Job-to-Be-Done Marketplace platform.

This file defines the SQLAlchemy models that represent the database schema
for the application.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """
    User model representing both clients and contractors in the system.
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_contractor = db.Column(db.Boolean, default=False)
    skills = db.Column(db.String(500))
    bio = db.Column(db.Text)
    profile_image = db.Column(db.String(200))
    stripe_customer_id = db.Column(db.String(100))
    stripe_connect_id = db.Column(db.String(100))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    jobs = db.relationship('Job', backref='client', lazy=True)
    tasks_assigned = db.relationship('Task', backref='contractor', lazy=True)
    applications = db.relationship('Application', backref='contractor', lazy=True)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Job(db.Model):
    """
    Job model representing a client's problem/project.
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    budget = db.Column(db.Float, nullable=False)
    timeline = db.Column(db.Integer, nullable=False)  # In days
    status = db.Column(db.String(50), default='pending')  # pending, planning, in-progress, completed
    success_criteria = db.Column(db.Text)
    progress = db.Column(db.Integer, default=0)  # 0 to 100
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_completed = db.Column(db.DateTime)
    
    # Relationships
    tasks = db.relationship('Task', backref='job', lazy=True)
    payments = db.relationship('Payment', backref='job', lazy=True)
    
    def __repr__(self):
        return f'<Job {self.title}>'
    
    def update_progress(self):
        """
        Calculate and update the job progress based on completed tasks
        """
        if not self.tasks:
            self.progress = 0
            return
        
        completed_tasks = sum(1 for task in self.tasks if task.status == 'completed')
        self.progress = int((completed_tasks / len(self.tasks)) * 100)
        
        if self.progress == 100:
            self.status = 'completed'
            self.date_completed = datetime.utcnow()

class Task(db.Model):
    """
    Task model representing a decomposed part of a job.
    """
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    contractor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    budget = db.Column(db.Float, nullable=False)
    timeline = db.Column(db.Integer, nullable=False)  # In days
    status = db.Column(db.String(50), default='open')  # open, assigned, in-progress, completed
    skills_required = db.Column(db.String(500))
    difficulty = db.Column(db.String(20))  # easy, medium, hard
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_assigned = db.Column(db.DateTime)
    deadline = db.Column(db.DateTime)
    date_completed = db.Column(db.DateTime)
    
    # Relationships
    applications = db.relationship('Application', backref='task', lazy=True)
    payments = db.relationship('Payment', backref='task', lazy=True)
    
    def __repr__(self):
        return f'<Task {self.title}>'

class Application(db.Model):
    """
    Application model representing a contractor's application for a task.
    """
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    contractor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, accepted, rejected
    proposal = db.Column(db.Text)
    date_applied = db.Column(db.DateTime, default=datetime.utcnow)
    date_reviewed = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Application {self.id} for Task {self.task_id}>'

class Payment(db.Model):
    """
    Payment model representing financial transactions in the system.
    """
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    fee = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), nullable=False)  # pending, completed, failed
    type = db.Column(db.String(50), nullable=False)  # deposit, payment, refund
    stripe_payment_id = db.Column(db.String(100))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_processed = db.Column(db.DateTime)
    
    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id])
    recipient = db.relationship('User', foreign_keys=[recipient_id])
    
    def __repr__(self):
        return f'<Payment {self.id} for {self.amount}>'

class Notification(db.Model):
    """
    Notification model for user notifications.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # info, success, warning, error
    read = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(200))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.id} for User {self.user_id}>'

class Review(db.Model):
    """
    Review model for contractor and job reviews.
    """
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    task = db.relationship('Task')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id])
    reviewee = db.relationship('User', foreign_keys=[reviewee_id])
    
    def __repr__(self):
        return f'<Review {self.id} - Rating: {self.rating}>'
