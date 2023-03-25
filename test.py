from dbModels import db, Naam, Kenmerk, Toepassing
from app import app
namen = [(r[0], r[1]) for r in db.session.query(Naam.id, Naam.naam).all()]
print(namen)
for i in namen:
    print(type(i))
test = db.session.query(Naam).get('2')
print(test.toepassingen)