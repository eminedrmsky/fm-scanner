from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from dataclasses import dataclass

db = SQLAlchemy()
ma = Marshmallow()


#SQLAlchemy modelleri
class status(db.Model):
    freq    = db.Column(db.Integer, unique = True, primary_key=True)
    kanal   = db.Column(db.Text)
    resp1 	= db.Column(db.Integer)
    rssi 	= db.Column(db.Integer)
    snr 	= db.Column(db.Integer)
    stat 	= db.Column(db.Text)

    def __init__(self, freq, kanal, resp1, rssi, snr, stat):
        self.freq = freq
        self.kanal = kanal
        self.resp1 = resp1
        self.rssi = rssi
        self.snr = snr
        self.stat = stat

class ParameterSchema(ma.Schema):
    class Meta:
        fields = ('freq', 'kanal', 'resp1', 'rssi', 'snr', 'stat')

parameter_schema = ParameterSchema()
parameters_schema = ParameterSchema(many = True)

#data schema
class data(db.Model):
    date    = db.Column(db.Text, primary_key=True)
    freq   = db.Column(db.Integer)
    resp1 	= db.Column(db.Integer)
    rssi 	= db.Column(db.Integer)
    snr 	= db.Column(db.Integer)
    info 	= db.Column(db.Text)
    temp = db.Column(db.Integer)
    hum = db.Column(db.Integer)

    def __init__(self, freq, date, resp1, rssi, snr, info, temp, hum):
        self.freq = freq
        self.date = date
        self.resp1 = resp1
        self.rssi = rssi
        self.snr = snr
        self.info = info
        self.temp = temp
        self.hum = hum

class dataSchema(ma.Schema):
    class Meta:
        fields = ('date','freq',  'resp1', 'rssi', 'snr', 'info', 'temp', 'hum')

data_schema = dataSchema()
datas_schema = dataSchema(many = True)


#mediums schema
class medium(db.Model):
    date = db.Column(db.String(20), primary_key = True)
    temp = db.Column(db.Integer)
    hum = db.Column(db.Integer)

    
    def __init__(self, date, temp, hum):
        self.date = date
        self.temp = temp
        self.hum = hum

class MediumSchema(ma.Schema):
    class Meta:
        fields = ('date', 'temp', 'hum')

medium_schema = MediumSchema(many = True)


#recods tablosu
@dataclass
class records(db.Model):
    name      = db.Column(db.Text, primary_key = True)
    length    = db.Column(db.Integer)
    info 	= db.Column(db.Text)

class RecordsSchema(ma.Schema):
    class Meta:
        fields = ('name', 'length', 'info')

records_schema = RecordsSchema(many = True)
record_schema = RecordsSchema()


#dinleme tablosu
class dinleme(db.Model):
    var = db.Column(db.String(20), primary_key = True)
    stat = db.Column(db.Integer)
    
   
    def __init__(self, var, stat):
        self.var = var
        self.stat = stat


#Power table

class power(db.Model):
    date    = db.Column(db.String(20), primary_key = True)
    info 	= db.Column(db.Text)

    def __init__(self, date, info):
        self.date = date
        self.info = info
        

class PowerSchema(ma.Schema):
    class Meta:
        fields = ('date',  'info')

powers_schema = PowerSchema(many = True)
power_schema = PowerSchema()
       

