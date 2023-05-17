from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from flask_bootstrap import Bootstrap
from flask_session import Session

from lists import list_of_test_materials

from google.cloud import secretmanager

from dbModels import db, Naam, Kenmerk, Toepassing, Select_RAL, Select_NLSFB
from forms import BaseSelections
import pprint as pp


app = Flask(__name__)

# connect the SQL lite db to Flask
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///NaamKenmerkToepassing.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


def get_secret(secret_name):
    client = secretmanager.SecretManagerServiceClient()
    secret_version_name = f"projects/naamkenmerktoepassing/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": secret_version_name})
    return response.payload.data.decode("UTF-8")


# some flask config
app.config['SECRET_KEY'] = get_secret("Flask_Secret_Key")
app.config['SESSION_TYPE'] = 'filesystem'
db.init_app(app)
Bootstrap(app)
app.app_context().push()
Session(app)


# function to check if session cookie contains extra fields key. If not make it and return true
def extra_fields():
    if 'extra_fields' not in session:
        session['extra_fields'] = {}
    return True


# returns the correct naam from the database by id
def get_naam(_id: int) -> 'Naam element':
    return Naam.query.filter_by(id=_id).first()


# returns the correct kenmerk from the database by id
def get_kenmerk(_id: int) -> 'Kenmerk element':
    return Kenmerk.query.filter_by(id=_id).first()


# returns the correct toepassing from the database by id
def get_toepassing(_id: int) -> 'Toepassing element':
    return Toepassing.query.filter_by(id=_id).first()


# create a string with the correct material name
def create_material(n: int, k: int, t: int, extra=[]) -> str:
    n_element = get_naam(n)
    k_element = get_kenmerk(k)
    t_element = get_toepassing(t)
    extra_string = ''
    for _string in extra:
        clean_string = _string.replace('.', '').replace(' ', '-').lower()
        extra_string += f'_{clean_string}'
    _string = f'{n_element.naam}_{k_element.kenmerk}_{t_element.toepassing}{extra_string}'
    print(_string, extra)
    return _string

# Main page
@app.route('/', methods=['GET', 'POST'])
def index():

    # creates a materials list in the session cookie if not already exits
    if 'created_materials' not in session:
        session['created_materials'] = []
    created_materials = session['created_materials']

    # extra class needed for the forms to work correctly with FieldList
    class F(BaseSelections):
        pass
    formulier = F()

    # check if site already in use. If so use last inputs as default else make first choice as default.
    if 'current' in session:
        naam_selection = session['current']['naam_selection']
        formulier.naam_selection.choices = [(r[0], r[1]) for r in db.session.query(Naam.id, Naam.naam).all()]
        formulier.naam_selection.data = int(session['current']['naam_selection'])
        formulier.kenmerk_selection.choices = [(ken.id, ken.kenmerk) for ken in get_naam(naam_selection).kenmerken]
        formulier.kenmerk_selection.data = int(session['current']['kenmerk_selection'])
        formulier.toepassing_selection.choices = [(toe.id, toe.toepassing) for toe in get_naam(naam_selection).toepassingen]
        formulier.toepassing_selection.data = int(session['current']['toepassing_selection'])
        extra = []
        for extra_field in session['extra_fields'].values():
            if 'value' in extra_field.keys():
                extra.append(extra_field['value'])
        materiaal_naam = create_material(n=formulier.naam_selection.data,
                                         k=formulier.kenmerk_selection.data,
                                         t=formulier.toepassing_selection.data,
                                         extra=extra)

    else:
        session['current'] = {}
        formulier.naam_selection.choices = [(r[0], r[1]) for r in db.session.query(Naam.id, Naam.naam).all()]
        formulier.naam_selection.data = 1
        formulier.kenmerk_selection.choices = [(ken.id, ken.kenmerk) for ken in get_naam(1).kenmerken]
        formulier.kenmerk_selection.data = 1
        formulier.toepassing_selection.choices = [(toe.id, toe.toepassing) for toe in get_naam(1).toepassingen]
        formulier.toepassing_selection.data = 1
        materiaal_naam = create_material(n=1, k=1, t=1, extra=[])
        session['current']['naam_selection'] = 1
        session['current']['kenmerk_selection'] = 1
        session['current']['toepassing_selection'] = 1
        session['current']['material_name'] = materiaal_naam

    # create extra fields by looking up how many are needed from the session cookie

    if extra_fields():
        ef = session['extra_fields']
        drop_list = {'drop-items': {'input': 'Vrij invulveld', 'nlsfb': 'NL-SfB', 'select_ral': 'RAL kleur'}}
        drop_list['extra_fields'] = {}
        for field in ef.values():
            print(field)
            if field['type'] in ['nlsfb', 'select_ral']:
                drop_list['extra_fields'][field['type']] = field['id']
        print(drop_list)
        print(ef)

    materials_list = []
    for i in created_materials:
        materials_list.append([i])

    return render_template('index.html', formulier=formulier, selections=materials_list, materiaal=materiaal_naam,
                           extra_fields=ef, drop_list=drop_list)


# used by JS for getting the available choices when the NAAM selection chainges.
@app.route('/naam/<num>')
def update(num):
    filter_naam = Naam.query.filter_by(id=num).first()
    print(filter_naam.naam)
    kenmerken = [{'id': k.id, 'kenmerk': k.kenmerk} for k in filter_naam.kenmerken]
    toepassingen = [{'id': t.id, 'toepassing': t.toepassing} for t in filter_naam.toepassingen]
    session['naam_selected'] = num
    return jsonify({'kenmerken': kenmerken, 'toepassingen': toepassingen})


# used by JS for getting a new material name for when an input in the form changes
@app.route('/material')
def material():
    session['current'] = request.args.to_dict()
    n = request.args.get('naam_selection', default=1, type=int)
    k = request.args.get('kenmerk_selection', default=1, type=int)
    t = request.args.get('toepassing_selection', default=1, type=int)
    print('args', request.args.to_dict())

    if extra_fields():
        print(session['extra_fields'])
    extra = []

    result = {}

    for _k, _v in request.args.to_dict().items():
        if _k[-9:].lower() not in ["selection", 'nlsfb'] and len(_v) > 0:
            extra.append(_v)
            session['extra_fields'][_k.split('-')[-1]]['value'] = _v
        elif _k == 'nlsfb':
            search = create_material(n=n, k=k, t=1)[:-4]
            nlsfb_code = Select_NLSFB.query.filter_by(materiaal=search).first()
            print(nlsfb_code)
            if nlsfb_code is not None:
                result['nlsfb'] = nlsfb_code.nlsfb
                extra.append(nlsfb_code.nlsfb)
            else:
                result['nlsfb'] = '[geen code]'

    result['material'] = create_material(n=n, k=k, t=t, extra=extra)
    session['current']['material_name'] = result['material']

    return jsonify(result)


# adds a material name to the list for when 'save' is selected
@app.route('/add')
def add_item():
    if session['current']['material_name'] not in session['created_materials']:
        session['created_materials'].insert(0, session['current']['material_name'])
    else:
        flash(f"{session['current']['material_name']} is al in de lijst opgenomen")
        print('already in list')
    return redirect(url_for('index'))


# deletes an entry from the material names list
@app.route('/del/<_index>')
def delete_item(_index):
    if _index.isdigit() and 'created_materials' in session:
        real_index = len(session['created_materials']) - int(_index)
        print('deleting: ', session['created_materials'][real_index])
        del session['created_materials'][real_index]
    else:
        print(_index, 'is of type', type(_index), 'not int')
    return redirect(url_for('index'))


#removes entire material list
@app.route('/del_list')
def delete_list():
    pp.pprint(session['created_materials'])
    session['created_materials'] = []
    return redirect((url_for('index')))


# adds an extra entry in the fields session cookie. Later the main index uses it to add an extra input box
@app.route('/add_field')
def add_field():
    if len(session['extra_fields']) == 0:
        c = '1'
    else:
        _ints = [int(i) for i in session['extra_fields'].keys()]
        c = str(max(_ints) + 1)
    session['extra_fields'][c] = {'name': f'extra_fields-{c}',
                                  'label': f'Extra {c}',
                                  'type': 'input',
                                  'id': str(c)}
    return redirect(url_for('index'))


@app.route('/remove_field/<_index>')
def remove_field(_index):
    """function to remove an extra field when [-] button is selected"""
    print("removing:", _index)
    if extra_fields():
        if _index in session['extra_fields']:
            del session['extra_fields'][_index]
    return redirect(url_for('index'))


@app.route('/extrafieldlist/<_index>/<_type>')
def extra_field_list(_index, _type):
    """function to change an extra field from an input to something else or back"""
    print("got index: ", _index, 'and type: ', _type)
    current_field = session['extra_fields'][_index]
    current_field['type'] = _type
    current_field.pop('value', None)
    current_field.pop('select_list', None)
    if _type[:6] == 'select':
        if _type[7:] == 'ral':
            current_field['select_list'] = [r[0] for r in db.session.query(Select_RAL.nummer).all()]
            current_field['value'] = current_field['select_list'][0]

    if _type == 'nlsfb':
        search = '_'.join(session['current']['material_name'].split('_', 2)[:2])
        nlsfb_code = Select_NLSFB.query.filter_by(materiaal=search).first()
        if nlsfb_code is not None:
            current_field['value'] = nlsfb_code.nlsfb

    print(session['extra_fields'])
    return redirect(url_for('index'))

#add some testing data
@app.route('/add_temp_list')
def temp():
    session['created_materials'] = list_of_test_materials


if __name__ == '__main__':
    app.run(debug=True)
