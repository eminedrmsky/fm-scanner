from flask import Flask, render_template, jsonify, request, Response
from flask_restful import Api, Resource, reqparse
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
import urllib.request, json

app = Flask(__name__, static_folder='static')
api = Api(app)

app.config["SECRET_KEY"] = "abefmscanner"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///FMdatabase.db'

db = SQLAlchemy(app)
ma = Marshmallow(app)

urlbase="http://192.168.1.28:3000"

#SQLAlchemy modelleri
#table which  records frequencies and channel names###############################
class frequencies(db.Model):
    freq    = db.Column(db.Integer, unique = True, primary_key=True)
    Kanal   = db.Column(db.Text)

    def __init__(self, freq, Kanal):
        self.freq = freq
        self.Kanal = Kanal

class frequencySchema(ma.Schema):
    class Meta:
        fields = ('freq', 'Kanal')

frequency_schema = frequencySchema()
frequencies_schema = frequencySchema(many = True)


#Table with channel datas ###########################################################
class frequencyData(db.Model):
    freq    = db.Column(db.Integer, unique = True, primary_key=True)
    resp1   = db.Column(db.Integer)
    rssi   = db.Column(db.Integer)
    snr   = db.Column(db.Integer)

    def __init__(self, freq, resp1, rssi, snr):
        self.freq = freq
        self.resp1 = resp1
        self.rssi = rssi
        self.snr = snr

class parameterSchema(ma.Schema):
    class Meta:
        fields = ('freq', 'resp1', 'rssi', 'snr')

parameter_schema = parameterSchema()
parameter_schema = parameterSchema(many = True)


#TODO sonra yapılcak medium  ve records


# class medium(db.Model):
#     date = db.Column(db.String(20), primary_key = True)
#     temp = db.Column(db.Integer)
#     hum = db.Column(db.Integer)

    
#     def __init__(self, date, temp, hum):
#         self.date = date
#         self.temp = temp
#         self.hum = hum

# class MediumSchema(ma.Schema):
#     class Meta:
#         fields = ('date', 'temp', 'hum')

# medium_schema = MediumSchema(many = True)

# class records(db.Model):
#     name      = db.Column(db.Text, primary_key = True)
#     length    = db.Column(db.Integer)
#     info 	= db.Column(db.Text)

# class RecordsSchema(ma.Schema):
#     class Meta:
#         fields = ('name', 'length', 'info')

# records_schema = RecordsSchema(many = True)
# record_schema = RecordsSchema()

#####################################################################################################################################################


#class for manipulating only one channel entry and its parameters#######################
class Frequency(Resource):
#gets data of chosen frequency
    def get(self, frequency):
        parameters = status.query.get(frequency)
        return parameter_schema.jsonify(parameters)

#adds new frequency to database 
    def post(self,frequency):    

        freq = request.json['freq']
        Kanal = request.json['Kanal']
        resp1 = request.json['resp1']
        rssi = request.json['rssi']
        snr = request.json['snr']
        stat = request.json['stat']

        new_frequency = status(freq, Kanal, resp1, rssi, snr, stat)

        db.session.add(new_frequency)
        db.session.commit()

        return parameter_schema.jsonify(new_frequency)
#updates all data of chosen frequency
    def put(self, frequency):
        parameters = status.query.get(frequency)

        freq = request.json['freq']
        Kanal = request.json['Kanal']
        resp1 = request.json['resp1']
        rssi = request.json['rssi']
        snr = request.json['snr']
        stat = request.json['stat']

        parameters.freq = freq
        parameters.Kanal = Kanal
        parameters.resp1 = resp1
        parameters.rssi = rssi
        parameters.snr = snr
        parameters.stat = stat

        db.session.commit()

        return parameter_schema.jsonify(parameters)

#deletes chosen frequency from database
    def delete(self, frequency):
        parameters = status.query.get(frequency)
        db.session.delete(parameters)
        db.session.commit()
        return parameter_schema.jsonify(parameters)

# class for manipulating all channel datas and their parameters###################################
class allFrequencies(Resource):
    def get(self):
        #all_Frequencies = status.query.all()
        all_Frequencies = frequencies.query.all()
        result = frequencies_schema.dump(all_Frequencies)
        return jsonify(result)
    
    def post(self):
        return {}

    def put(self):
        return{}
    
    def delete(self):
        return {}

#class for manipulating temperature and humidity data that taken from device regularly##############
class temperatureAndHumidity(Resource):
    def get(self):
        parameters = medium.query.all()
        result = medium_schema.dump(parameters)
        return jsonify(result)
    
    def post(self):
        date = request.json['date']
        temp = request.json['temp']
        hum = request.json['hum']

        new_medium = status(date,temp,hum)

        db.session.add(new_medium)
        db.session.commit()

        return medium_schema.jsonify(new_medium)


    def put(self):
        return{}

    def delete(self):
        return {}

class isThereSound(Resource):
    def get(self):
        return{}

class isThereConnection(Resource):
    def get(self):
        return{}

class searchChannel(Resource):
    def get(self):
        return{}

#class for manipulating only one channel entry and its parameters#######################
class Records(Resource):
#gets data of all records
    def get(self):
        all_records = records.query.all()
        result = records_schema.dump(all_records)
        return jsonify(result)

#deletes chosen record from database
class delete_record(Resource):
    def delete(self, record):
        Record_info = records.query.get(record)
        db.session.delete(Record_info)
        db.session.commit()
        return record_schema.jsonify(Record_info)

##########################Resources and routes ###############################################################################################################################


api.add_resource(Frequency, "/frequency/<int:frequency>")
api.add_resource(allFrequencies, "/parameters")
api.add_resource(temperatureAndHumidity, "/tempAndHum")
api.add_resource(isThereSound, "/sound")
api.add_resource(isThereConnection, "/connection")
api.add_resource(searchChannel, "/search")
api.add_resource(Records, "/records")
api.add_resource(delete_record, "/records/<string:record>")

if __name__ == '__main__':
    app.run( host='0.0.0.0', debug= False, threaded=True, port=8000)


