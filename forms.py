from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class YourProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    institution = StringField('Institution', validators=[DataRequired(), Length(min=2, max=100)])
    degree = StringField('Degree', validators=[DataRequired(), Length(min=2, max=100)])
    graduation_year = StringField('Graduation Year', validators=[DataRequired(), Length(min=2, max=100)])
    skill_name = StringField('Skill Name', validators=[DataRequired(), Length(min=2, max=100)])
    proficiency_level = StringField('Proficiency_level', validators=[DataRequired(), Length(min=2, max=100)])
    referee_name = StringField('Referee name', validators=[DataRequired(), Length(min=2, max=100)])
    referee_email = StringField('Referee email', validators=[DataRequired(), Length(min=2, max=100)])
    phone_number = StringField('Phone number', validators=[DataRequired(), Length(min=2, max=100)])
    relationship = StringField('Relationship', validators=[DataRequired(), Length(min=2, max=100)])
    
    # Add other fields as needed
    submit = SubmitField('Save Changes')