from flask import Flask, render_template, request, jsonify, request, redirect, url_for, session
from flask_wtf import Form
from wtforms import SelectField
from flask_bootstrap import Bootstrap
from flask_session import Session

from dbModels import db, Naam, Kenmerk, Toepassing
from forms import BaseSelections

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///NaamKenmerkToepassing.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '5097bb62-06fb-4099-8633-78767a79f90b'
app.config['SESSION_TYPE'] = 'filesystem'
db.init_app(app)
Bootstrap(app)
app.app_context().push()
Session(app)


def get_naam(_id: int):
    return Naam.query.filter_by(id=_id).first()


def get_kenmerk(_id: int):
    return Kenmerk.query.filter_by(id=_id).first()


def get_toepassing(_id: int):
    return Toepassing.query.filter_by(id=_id).first()


def create_material(n: int, k: int, t: int) -> str:
    n_element = get_naam(n)
    k_element = get_kenmerk(k)
    t_element = get_toepassing(t)
    return f'{n_element.naam}_{k_element.kenmerk}_{t_element.toepassing}'


@app.route('/', methods=['GET', 'POST'])
def index():

    if 'created_materials' not in session:
        session['created_materials'] = []
    created_materials = session['created_materials']

    formulier = BaseSelections()

    if formulier.is_submitted():

        selection_naam = get_naam(formulier['naam_selection'].data)
        selection_kenmerk = get_kenmerk(formulier['kenmerk_selection'].data)
        selection_toepassing = get_toepassing(formulier['toepassing_selection'].data)
        created_materials.insert(0, f'{selection_naam.naam}_{selection_kenmerk.kenmerk}_{selection_toepassing.toepassing}')
        kenmerken = [(ken.id, ken.kenmerk) for ken in selection_naam.kenmerken]
        toepassingen = [(toe.id, toe.toepassing) for toe in selection_naam.toepassingen]
    else:
        kenmerken = [(r[0], r[1]) for r in db.session.query(Kenmerk.id, Kenmerk.kenmerk).all()]
        toepassingen = [(r[0], r[1]) for r in db.session.query(Toepassing.id, Toepassing.toepassing).all()]

    namen = [(r[0], r[1]) for r in db.session.query(Naam.id, Naam.naam).all()]

    formulier.naam_selection.choices = namen
    formulier.naam_selection.default = 0 if not formulier.is_submitted() else formulier['naam_selection'].data - 1
    formulier.kenmerk_selection.choices = kenmerken
    formulier.kenmerk_selection.default = 0 if not formulier.is_submitted() else formulier['kenmerk_selection'].data - 1
    formulier.toepassing_selection.choices = toepassingen
    formulier.toepassing_selection.default = 0 if not formulier.is_submitted() else formulier['toepassing_selection'].data - 1
    materiaal = created_materials[0] if len(created_materials) > 0 else 'ntb_ntb_ntb'
    return render_template('index.html', formulier=formulier, selections=created_materials, materiaal=materiaal)


@app.route('/naam/<num>')
def update(num):
    filter_naam = Naam.query.filter_by(id=num).first()
    print(filter_naam.naam)
    kenmerken = [{'id': k.id, 'kenmerk': k.kenmerk} for k in filter_naam.kenmerken]
    toepassingen = [{'id': t.id, 'toepassing': t.toepassing} for t in filter_naam.toepassingen]

    return jsonify({'kenmerken': kenmerken, 'toepassingen': toepassingen})


@app.route('/material')
def material():
    n = request.args.get('naam', default=" ", type=int)
    k = request.args.get('kenmerk', default=" ", type=int)
    t = request.args.get('toepassing', default=" ", type=int)

    return jsonify({'material': create_material(n=n, k=k, t=t)})


@app.route('/del/<_index>')
def delete_item(_index):
    if _index.isdigit() and 'created_materials' in session:
        del session['created_materials'][int(_index)]
    else:
        print(_index, 'is of type', type(_index), 'not int')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
