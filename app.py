from flask import Flask, render_template, request, jsonify
from flask_wtf import Form
from wtforms import SelectField
from flask_bootstrap import Bootstrap

from dbModels import db, Naam, Kenmerk, Toepassing
from forms import BaseSelections

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///NaamKenmerkToepassing.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '5097bb62-06fb-4099-8633-78767a79f90b'
db.init_app(app)
Bootstrap(app)
app.app_context().push()

selections = []


@app.route('/', methods=['GET', 'POST'])
def index():
    formulier = BaseSelections()

    if formulier.is_submitted():

        selection_naam = Naam.query.filter_by(id = formulier['naam_selection'].data).first()
        selection_kenmerk = Kenmerk.query.filter_by(id=formulier['kenmerk_selection'].data).first()
        selection_toepassing = Toepassing.query.filter_by(id=formulier['toepassing_selection'].data).first()
        selections.append(f'{selection_naam.naam}_{selection_kenmerk.kenmerk}_{selection_toepassing.toepassing}')
        kenmerken = [(ken.id, ken.kenmerk) for ken in selection_naam.kenmerken]
        toepassingen = [(toe.id, toe.toepassing) for toe in selection_naam.toepassingen]

    else:
        kenmerken = [(r[0], r[1]) for r in db.session.query(Kenmerk.id, Kenmerk.kenmerk).all()]
        toepassingen = [(r[0], r[1]) for r in db.session.query(Toepassing.id, Toepassing.toepassing).all()]
    namen = [(r[0], r[1]) for r in db.session.query(Naam.id, Naam.naam).all()]

    formulier.naam_selection.choices = namen
    formulier.kenmerk_selection.choices = kenmerken
    formulier.toepassing_selection.choices = toepassingen
    return render_template('index.html', formulier=formulier, selections=selections)


@app.route('/naam/<num>')
def update(num):
    print('naam', num)
    filter_naam = Naam.query.filter_by(id = num).first()
    print(filter_naam.naam)
    kenmerken = [{'id': k.id, 'kenmerk': k.kenmerk} for k in filter_naam.kenmerken]
    toepassingen = [{'id': t.id, 'toepassing': t.toepassing} for t in filter_naam.toepassingen]

    return jsonify({'kenmerken': kenmerken, 'toepassingen': toepassingen})


if __name__ == '__main__':
    app.run(debug=True)
