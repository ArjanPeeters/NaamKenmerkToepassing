from flask import Flask, render_template, request, jsonify, request, redirect, url_for, session
from wtforms import StringField
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

current_material = ''


def extra_fields():
    if 'extra_fields' not in session:
        session['extra_fields'] = {}
    return True


def get_naam(_id: int) -> 'Naam element':
    return Naam.query.filter_by(id=_id).first()


def get_kenmerk(_id: int) -> 'Kenmerk element':
    return Kenmerk.query.filter_by(id=_id).first()


def get_toepassing(_id: int) -> 'Toepassing element':
    return Toepassing.query.filter_by(id=_id).first()


def create_material(n: int, k: int, t: int, extra: list) -> str:
    n_element = get_naam(n)
    k_element = get_kenmerk(k)
    t_element = get_toepassing(t)
    extra_string = ''
    for a in extra:
        extra_string += f'_{a}'
    _string = f'{n_element.naam}_{k_element.kenmerk}_{t_element.toepassing}{extra_string}'
    print(_string, extra)
    return _string


@app.route('/', methods=['GET', 'POST'])
def index():

    if 'created_materials' not in session:
        session['created_materials'] = []
    created_materials = session['created_materials']

    class F(BaseSelections):
        pass
    formulier = F()

    if formulier.is_submitted():

        naam_id = formulier['naam_selection'].data
        kenmerk_id = formulier['kenmerk_selection'].data
        toepassing_id = formulier['toepassing_selection'].data
        extra = formulier['extra_fields']
        print(extra)
        extra = []
        for entry in formulier.extra_fields:
            extra.append(entry.data)
            print(entry)
            session['extra_fields'][entry.id.split('-')[-1]]['value'] = entry.data
        created_materials.insert(0, create_material(n=naam_id, k=kenmerk_id, t=toepassing_id, extra=extra))
        kenmerken = [(ken.id, ken.kenmerk) for ken in get_naam(naam_id).kenmerken]
        toepassingen = [(toe.id, toe.toepassing) for toe in get_naam(naam_id).toepassingen]
    else:
        kenmerken = [(r[0], r[1]) for r in db.session.query(Kenmerk.id, Kenmerk.kenmerk).all()]
        toepassingen = [(r[0], r[1]) for r in db.session.query(Toepassing.id, Toepassing.toepassing).all()]

    namen = [(r[0], r[1]) for r in db.session.query(Naam.id, Naam.naam).all()]

    # fill the form with the data
    formulier.naam_selection.choices = namen
    formulier.naam_selection.default = 0 if not formulier.is_submitted() else formulier['naam_selection'].data - 1
    formulier.kenmerk_selection.choices = kenmerken
    formulier.kenmerk_selection.default = 0 if not formulier.is_submitted() else formulier['kenmerk_selection'].data - 1
    formulier.toepassing_selection.choices = toepassingen
    formulier.toepassing_selection.default = 0 if not formulier.is_submitted() else formulier['toepassing_selection'].data - 1
    materiaal = created_materials[0] if len(created_materials) > 0 else 'ntb_ntb_ntb'

    # create extra fields
    if extra_fields():
        c = 0
        if len(formulier.extra_fields) > 0:
            for field in range(len(formulier.extra_fields)):
                formulier.extra_fields.pop_entry()
        for _number, _item in session["extra_fields"].items():
            formulier.extra_fields.append_entry()
            formulier.extra_fields[c].label = _item['label']
            formulier.extra_fields[c].data = _item['value'] if 'value' in _item else ''
            formulier.extra_fields[c].name = _item['name']
            formulier.extra_fields[c].id = _number
            print(session['extra_fields'])
            c += 1

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
    n = request.args.get('naam_selection', default=1, type=int)
    k = request.args.get('kenmerk_selection', default=1, type=int)
    t = request.args.get('toepassing_selection', default=1, type=int)
    print('args', request.args.to_dict())
    print(session['extra_fields'])
    extra = []
    for _k, _v in request.args.to_dict().items():
        if _k[:5].lower() == "extra" and len(_v) > 0:
            extra.append(_v)
            session['extra_fields'][_k.split('-')[-1]]['value'] = _v
    return jsonify({'material': create_material(n=n, k=k, t=t, extra=extra)})


@app.route('/del/<_index>')
def delete_item(_index):
    if _index.isdigit() and 'created_materials' in session:
        del session['created_materials'][int(_index)]
    else:
        print(_index, 'is of type', type(_index), 'not int')
    return redirect(url_for('index'))


@app.route('/add_field')
def add_field():
    if len(session['extra_fields']) == 0:
        c = '1'
    else:
        _ints = [int(i) for i in session['extra_fields'].keys()]
        c = str(max(_ints) + 1)
    session['extra_fields'][c] = {'name': f'extra_fields-{c}',
                                  'label': f'Extra {c}'}
    return redirect(url_for('index'))


@app.route('/remove_field/<_index>')
def remove_field(_index):
    i = _index
    print("removing:", i)
    if extra_fields():
        if i in session['extra_fields']:
            del session['extra_fields'][i]
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
