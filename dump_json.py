"""NaamKenmerkToepassing.db -> static/data.json

Dumpt de vaste referentiedata (naam/kenmerk/toepassing + koppeltabellen, RAL,
NL-SfB) naar één statisch JSON-bestand, zodat de site zonder server/DB draait.

Gebruik:  python dump_json.py
Draai dit na import_excel.py, commit static/data.json en push.
"""
import json

from flask import Flask

from dbModels import db, Naam, Select_RAL, Select_NLSFB

DB_PATH = 'instance/NaamKenmerkToepassing.db'
OUT = 'static/data.json'


def build():
    namen = []
    for n in Naam.query.order_by(Naam.id).all():
        namen.append({
            'naam': n.naam,
            'kenmerken': [k.kenmerk for k in n.kenmerken],
            'toepassingen': [t.toepassing for t in n.toepassingen],
            'extra_lijsten': n.extra_lijst_dict(),  # {soort: [omschrijving, ...]}
        })

    ral = [{'nummer': r.nummer, 'omschrijving': r.omschrijving,
            'r': r.r, 'g': r.g, 'b': r.b}
           for r in Select_RAL.query.order_by(Select_RAL.nummer).all()]

    # 'naam_kenmerk' -> nlsfb-code
    nlsfb = {s.materiaal: s.nlsfb for s in Select_NLSFB.query.all()}

    return {'namen': namen, 'ral': ral, 'nlsfb': nlsfb}


def run():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH.split("/")[-1]}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        data = build()

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

    import os
    print(f'{OUT}: {len(data["namen"])} namen, {len(data["ral"])} RAL, '
          f'{len(data["nlsfb"])} nlsfb  ({os.path.getsize(OUT)} bytes)')


if __name__ == '__main__':
    run()
