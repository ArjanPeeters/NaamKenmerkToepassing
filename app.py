from flask import Flask, render_template, jsonify, request, redirect, url_for, session, Response
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
    for _string in extra:
        clean_string = _string.replace('.', '').lower()
        extra_string += f'_{clean_string}'
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

    """if formulier.is_submitted():

        naam_id = formulier['naam_selection'].data
        kenmerk_id = formulier['kenmerk_selection'].data
        toepassing_id = formulier['toepassing_selection'].data
        extra = []
        for entry in formulier.extra_fields:
            extra.append(entry.data)
            print(entry)
            session['extra_fields'][entry.id.split('-')[-1]]['value'] = entry.data

        materiaal_naam = create_material(n=naam_id, k=kenmerk_id, t=toepassing_id, extra=extra)
        created_materials.insert(0, materiaal_naam)
        kenmerken_choices = [(ken.id, ken.kenmerk) for ken in get_naam(naam_id).kenmerken]
        toepassingen_choices = [(toe.id, toe.toepassing) for toe in get_naam(naam_id).toepassingen]
    else:
        search_id = session['naam_selected'] if 'naam_selected' in session else 1
        print(search_id)
        kenmerken_choices = [(ken.id, ken.kenmerk) for ken in get_naam(search_id).kenmerken]
        toepassingen_choices = [(toe.id, toe.toepassing) for toe in get_naam(search_id).toepassingen]
        materiaal_naam = 'beton_ntb_ntb'
        
    namen_choices = [(r[0], r[1]) for r in db.session.query(Naam.id, Naam.naam).all()]

    # fill the form with the data
    formulier.naam_selection.choices = namen_choices
    formulier.naam_selection.default = 0 if not formulier.is_submitted() else formulier['naam_selection'].data - 1
    formulier.kenmerk_selection.choices = kenmerken_choices
    formulier.kenmerk_selection.default = 0 if not formulier.is_submitted() else formulier['kenmerk_selection'].data - 1
    formulier.toepassing_selection.choices = toepassingen_choices
    formulier.toepassing_selection.default = 0 if not formulier.is_submitted() else formulier['toepassing_selection'].data - 1
    
    """

    print(session)
    if 'current' in session:
        naam_selection = session['current']['naam_selection']
        formulier.naam_selection.choices = [(r[0], r[1]) for r in db.session.query(Naam.id, Naam.naam).all()]
        formulier.naam_selection.data = int(session['current']['naam_selection'])
        formulier.kenmerk_selection.choices = [(ken.id, ken.kenmerk) for ken in get_naam(naam_selection).kenmerken]
        formulier.kenmerk_selection.data = int(session['current']['kenmerk_selection'])
        formulier.toepassing_selection.choices = [(toe.id, toe.toepassing) for toe in get_naam(naam_selection).toepassingen]
        formulier.toepassing_selection.data = int(session['current']['toepassing_selection'])
        materiaal_naam = session['current']['material_name']

    else:
        formulier.naam_selection.choices = [(r[0], r[1]) for r in db.session.query(Naam.id, Naam.naam).all()]
        formulier.naam_selection.data = 0
        formulier.kenmerk_selection.choices = [(ken.id, ken.kenmerk) for ken in get_naam(1).kenmerken]
        formulier.kenmerk_selection.data = 0
        formulier.toepassing_selection.choices = [(toe.id, toe.toepassing) for toe in get_naam(1).toepassingen]
        formulier.toepassing_selection.data = 0
        materiaal_naam = 'beton_ntb_ntb'

    for i in ['naam', 'kenmerk', 'toepassing']:
        print(f'default {i}:', formulier[f'{i}_selection'].data)
        print(f'choices {i}', formulier[f'{i}_selection'].choices)


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

    return render_template('index.html', formulier=formulier, selections=created_materials, materiaal=materiaal_naam)


@app.route('/naam/<num>')
def update(num):
    filter_naam = Naam.query.filter_by(id=num).first()
    print(filter_naam.naam)
    kenmerken = [{'id': k.id, 'kenmerk': k.kenmerk} for k in filter_naam.kenmerken]
    toepassingen = [{'id': t.id, 'toepassing': t.toepassing} for t in filter_naam.toepassingen]
    session['naam_selected'] = num
    return jsonify({'kenmerken': kenmerken, 'toepassingen': toepassingen})


@app.route('/material')
def material():
    session['current'] = request.args.to_dict()
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
    material_name = create_material(n=n, k=k, t=t, extra=extra)
    session['current']['material_name'] = material_name
    return jsonify({'material': material_name})


@app.route('/add')
def add_item():
    session['created_materials'].insert(0, session['current']['material_name'])
    return redirect(url_for('index'))

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
