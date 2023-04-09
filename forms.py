from flask_wtf import FlaskForm
from wtforms import SelectField, FieldList, StringField
from wtforms.validators import input_required


class BaseSelections(FlaskForm):
    naam_selection = SelectField(u'Naam', coerce=int)
    kenmerk_selection = SelectField(u'Kenmerk', coerce=int)
    toepassing_selection = SelectField(u'Toepassing', coerce=int)
    extra_fields = FieldList(StringField())