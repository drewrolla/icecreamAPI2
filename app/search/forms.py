from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired

class IceCreamSearchForm(FlaskForm):
    location = StringField('Location', validators=[InputRequired()])
    submit = SubmitField()