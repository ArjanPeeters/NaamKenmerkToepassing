from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

naam_kenmerk_tabel = db.Table('naam_kenmerk',
                              db.Column('naam_id', db.Integer, db.ForeignKey('naam.id'), primary_key=True),
                              db.Column('kenmerk_id', db.Integer, db.ForeignKey('kenmerk.id'), primary_key=True))

naam_toepassing_tabel = db.Table('naam_toepassing',
                                 db.Column('naam_id', db.Integer, db.ForeignKey('naam.id'), primary_key=True),
                                 db.Column('toepassing_id', db.Integer, db.ForeignKey('toepassing.id'), primary_key=True))

naam_extra_lijsten_tabel = db.Table('naam_extra_lijsten',
                                    db.Column('naam_id', db.Integer, db.ForeignKey('naam.id'), primary_key=True),
                                    db.Column('Extralijsten_id', db.Integer, db.ForeignKey('extralijsten.id'), primary_key=True))


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
    extra_lijsten = db.relationship('ExtraLijsten',
                                    secondary=naam_extra_lijsten_tabel,
                                    lazy='subquery',
                                    backref=db.backref('namen', lazy=True))

    def __repr__(self):
        return f'Naam:{self.naam}, kenmerken: {len(self.kenmerken)}, toepassingen: {len(self.toepassingen)},' \
               f'extra lijsten: {len(self.extra_lijsten)}'

    def extra_lijst_dict(self):
        return_dict = {}
        for ele in self.extra_lijsten:
            if ele.soort in return_dict.keys():
                return_dict[ele.soort].append(ele.omschrijving)
            else:
                return_dict[ele.soort] = [ele.omschrijving]
        return return_dict


class Kenmerk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kenmerk = db.Column(db.String(25), index=True, unique=True)

    def __repr__(self):
        return f'Kenmerk:{self.kenmerk}, namen:{len(self.namen)}'


class Toepassing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    toepassing = db.Column(db.String(25), index=True, unique=True)

    def __repr__(self):
        return f'Toepassing:{self.toepassing}, namen:{len(self.namen)}'


class Select_RAL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nummer = db.Column(db.String(8), index=True, unique=True)
    r = db.Column(db.Integer)
    g = db.Column(db.Integer)
    b = db.Column(db.Integer)
    omschrijving = db.Column(db.String(20))

    def __repr__(self):
        return f'RAL: {self.nummer}, R{self.r} G{self.g} B{self.b}, -> {self.omschrijving}'


class Select_NLSFB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    materiaal = db.Column(db.String(40), index=True, unique=True)
    nlsfb = db.Column(db.String(5))

    def __repr__(self):
        return f'{self.materiaal}_{self.nlsfb}'


class ExtraLijsten(db.Model):
    __tablename__ = 'extralijsten'
    id = db.Column(db.Integer, primary_key=True)
    soort = db.Column(db.String(20))
    omschrijving = db.Column(db.String(25), index=True)

    def __repr__(self):
        return f'soort:{self.soort}, omschrijving: {self.omschrijving}, hoort bij:{self.namen}'
