from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

naam_kenmerk_tabel = db.Table('naam_kenmerk',
                              db.Column('naam_id', db.Integer, db.ForeignKey('naam.id'), primary_key=True),
                              db.Column('kenmerk_id', db.Integer, db.ForeignKey('kenmerk.id'), primary_key=True))

naam_toepassing_tabel = db.Table('naam_toepassing',
                                 db.Column('naam_id', db.Integer, db.ForeignKey('naam.id'), primary_key=True),
                                 db.Column('toepassing_id', db.Integer, db.ForeignKey('toepassing.id'), primary_key=True))


class Naam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    naam = db.Column(db.String(25), index=True, unique=True)
    kenmerken = db.relationship('Kenmerk',
                                secondary=naam_kenmerk_tabel,
                                lazy='subquery',
                                backref=db.backref('namen', lazy=True))
    toepassingen = db.relationship('Toepassing',
                                   secondary=naam_toepassing_tabel,
                                   lazy='subquery',
                                   backref=db.backref('namen', lazy=True))

    def __repr__(self):
        return f'Naam:{self.naam}, kenmerken:{self.kenmerken}, toepassingen:{self.toepassingen}'


class Kenmerk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kenmerk = db.Column(db.String(25), index=True, unique=True)

    def __repr__(self):
        return f'Kenmerk:{self.kenmerk}, namen:{self.namen}'


class Toepassing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    toepassing = db.Column(db.String(25), index=True, unique=True)

    def __repr__(self):
        return f'Toepassing:{self.toepassing}, namen:{self.namen}'


class KleurRAL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nummer = db.Column(db.String(8), index=True, unique=True)
    r = db.Column(db.Integer)
    g = db.Column(db.Integer)
    b = db.Column(db.Integer)
    omschrijving = db.Column(db.String(20))

    def __repr__(self):
        return f'RAL: {self.nummer}, R{self.r} G{self.g} B{self.b}, -> {self.omschrijving}'

