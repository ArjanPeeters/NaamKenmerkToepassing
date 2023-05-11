from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from flask_bootstrap import Bootstrap
from flask_session import Session

from google.cloud import secretmanager

from dbModels import db, Naam, Kenmerk, Toepassing
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
        materiaal_naam = session['current']['material_name']

    else:
        formulier.naam_selection.choices = [(r[0], r[1]) for r in db.session.query(Naam.id, Naam.naam).all()]
        formulier.naam_selection.data = 1
        formulier.kenmerk_selection.choices = [(ken.id, ken.kenmerk) for ken in get_naam(1).kenmerken]
        formulier.kenmerk_selection.data = 1
        formulier.toepassing_selection.choices = [(toe.id, toe.toepassing) for toe in get_naam(1).toepassingen]
        formulier.toepassing_selection.data = 1
        materiaal_naam = create_material(n=1, k=1, t=1, extra=[])

    # create extra fields by looking up how many are needed from the session cookie
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

    materials_list=[]
    for i in created_materials:
        materials_list.append([i])

    return render_template('index.html', formulier=formulier, selections=materials_list, materiaal=materiaal_naam)


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
    print(session['extra_fields'])
    extra = []
    for _k, _v in request.args.to_dict().items():
        if _k[:5].lower() == "extra" and len(_v) > 0:
            extra.append(_v)
            session['extra_fields'][_k.split('-')[-1]]['value'] = _v
    material_name = create_material(n=n, k=k, t=t, extra=extra)
    session['current']['material_name'] = material_name
    return jsonify({'material': material_name})


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


@app.route('/del_list')
def delete_list():
    pp.pprint(session['created_materials'])
    session['created_materials'] = []
    return redirect((url_for('index')))


@app.route('/add_temp_list')
def temp():
    session['created_materials'] =\
        ['organisch_bamboe_profiel',
         'organisch_bamboe_plaat',
         'organisch_bamboe_folie',
         'organisch_bamboe_ntb',
         'gips_stuc_generiek',
         'gips_stuc_prefab-element',
         'gips_anhydriet_prefab-element',
         'gips_balsa_vulling',
         'hout_balsa_vulling',
         'hout_balsa_stam',
         'hout_eiken_stam',
         'hout_generiek_tegel',
         'hout_bilinga_tegel',
         'hout_bilinga_ntb',
         'hout_bangkirai_ntb',
         'hout_bangkirai_schaaldeel',
         'hout_bangkirai_profiel',
         'hout_bangkirai_blok',
         'bitumen_asfalt_bedekking',
         'gips_generiek_ihw',
         'gips_generiek_bedekking',
         'gips_asfalt_bedekking',
         'bitumen_asfalt_ntb',
         'steenachtig_kunststeen_klinker_fghgv',
         'samengesteld_element_hek_fghgv',
         'isolatie_fenolhars_vulling_fghgv',
         'isolatie_fenolhars_ntb_fghgv',
         'isolatie_generiek_ntb_fghgv',
         'glas_generiek_ntb',
         'glas_gewapend_ntb',
         'cement_houtwolcement_ihw',
         'cement_generiek_ihw_rew',
         'cement_generiek_blok_rew',
         'gips_generiek_blok_rew',
         'gips_generiek_bedekking_rew',
         'gips_generiek_ihw_test',
         'gips_gipskarton_ihw_test',
         'grondstof_aarde_granulaat',
         'glas_cellulairglas_ntb',
         'glas_gasbeton_ntb',
         'beton_gasbeton_ntb']
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
                                  'label': f'Extra {c}'}
    return redirect(url_for('index'))


# Removes the entry for the extra input field from the session cookie
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
