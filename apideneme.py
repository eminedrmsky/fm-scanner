from flask import Flask, render_template, jsonify, request, Response
from flask_restful import Api, Resource, reqparse
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
import urllib.request, urllib.parse, json

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
    kanal   = db.Column(db.Text)

    def __init__(self, freq, kanal):
        self.freq = freq
        self.kanal = kanal

class frequencySchema(ma.Schema):
    class Meta:
        fields = ('freq', 'kanal')

frequency_schema = frequencySchema()
frequencies_schema = frequencySchema(many = True)


#Table with channel datas ###########################################################
class frequencyData(db.Model):
    freq    = db.Column(db.Integer, unique = True, primary_key=True)
    resp1 	= db.Column(db.Integer)
    rssi 	= db.Column(db.Integer)
    snr 	= db.Column(db.Integer)
    stat 	= db.Column(db.Text)
    kanal   = db.Column(db.Text)

    def __init__(self, freq, kanal, resp1, rssi, snr, stat):
        self.freq = freq
        self.kanal = kanal
        self.resp1 = resp1
        self.rssi = rssi
        self.snr = snr
        self.stat = stat

class dataSchema(ma.Schema):
    class Meta:
        fields = ('freq', 'kanal', 'resp1', 'rssi', 'snr', 'stat')

data_schema = dataSchema()
data_schema = dataSchema(many = True)


#####################################################################################################################################################
def getData():
    url = urlbase + "/parameters"
    response = urllib.request.urlopen(url)
    data = response.read()
    dict = json.loads(data)
    return dict

try:
    parameterData = getData()

    for parameter in parameterData:
        freq = parameter['freq']
        kanal = parameter['kanal']
        resp1 = parameter['resp1']
        rssi = parameter['rssi']
        snr = parameter['snr']
        stat = parameter['stat']
        new_frequency = frequencyData(freq, kanal, resp1, rssi, snr, stat)
        db.session.add(new_frequency)
        db.session.commit()

except Exception as e:
    print(e)


######################################################################################################################################################

# class for manipulating all channel datas and their parameters###################################
class allFrequencies(Resource):
    def get(self):
        all_Frequencies = frequencies.query.all()
        result = frequencies_schema.dump(all_Frequencies)
        return jsonify(result)
    
    def post(self):
        
        # for item in request
        # freq = request.json['freq']
        # kanal = request.json['kanal']
        # resp1 = 0
        # rssi = 0
        # snr = 0
        # stat = " "

        # new_frequency = status(freq, kanal, resp1, rssi, snr, stat)

        # db.session.add(new_frequency)
        # db.session.commit()

        # return parameter_schema.jsonify(new_frequency)
        return {}


##########################Resources and routes ###############################################################################################################################


api.add_resource(allFrequencies, "/frequencyData")

if __name__ == '__main__':
    app.run( host='0.0.0.0', debug= True, threaded=True, port=8000)


