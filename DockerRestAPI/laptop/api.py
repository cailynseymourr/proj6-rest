# Laptop Service
import csv
import io
from flask import Flask, Response, request
from flask_restful import Resource, Api, abort
from pymongo import MongoClient

# Instantiate the app
app = Flask(__name__)
api = Api(app)

client = MongoClient('db', 27017)
db = client.brevetsdb

class Laptop(Resource):
    def get(self):
        return {
            'Laptops': ['Mac OS', 'Dell', 
            'Windozzee',
	    'Yet another laptop!',
	    'Yet yet another laptop!'
            ]
        }
class ListTimes(Resource):
    fields = ["open", "close"]
    def get(self, fmt='json'):
        if fmt not in ("json", "csv"):
            abort(404)
        top = request.args.get("top", type=int)
        docs = list(db.controls.find({}, {"_id": 0}))
        docs.sort(key=lambda d: d['km'])
        if top is not None and top >= 0:
            docs = docs[:top]

        rows = [{f: d[f] for f in self.fields} for d in docs]

        if fmt == "csv":
            buf = io.StringIO()
            writer = csv.DictWriter(buf, fieldnames=self.fields)
            writer.writeheader()
            writer.writerows(rows)
            return Response(buf.getvalue(), mimetype="text/csv")

        return rows  # JSON is the default


class ListAll(ListTimes):
    fields = ["open", "close"]


class ListOpenOnly(ListTimes):
    fields = ["open"]


class ListCloseOnly(ListTimes):
    fields = ["close"]
# Create routes
# Another way, without decorators
api.add_resource(Laptop, '/')
api.add_resource(ListAll, '/listAll', '/listAll/<string:fmt>')
api.add_resource(ListOpenOnly, '/listOpenOnly', '/listOpenOnly/<string:fmt>')
api.add_resource(ListCloseOnly, '/listCloseOnly', '/listCloseOnly/<string:fmt>')

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
