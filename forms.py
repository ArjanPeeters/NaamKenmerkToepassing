from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.validators import input_required


class BaseSelections(FlaskForm):
    naam_selection = SelectField(u'Naam', coerce=int)
    kenmerk_selection = SelectField(u'Kenmerk', coerce=int)
    toepassing_selection = SelectField(u'Toepassing', coerce=int)