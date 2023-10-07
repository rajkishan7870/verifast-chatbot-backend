import json
from flask_cors import CORS
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
import pymongo


from general_util import setup_logger

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")  # Change the connection string as needed
db = mongo_client["Api_Message_Response"]  # Replace 'your_database_name' with your actual database name
collection = db["Response"]

try:
    import unzip_requirements
except ImportError:
    pass


chat_invocation_logger = setup_logger("chat_invocations", "./chat_invocations.log")

response_map = {
    'Hi': {
        'text': 'Hello from verifast!',
        'images': []
    },
    'show image': {
        'text': 'here are the images',
        'images': [
            'https://images.unsplash.com/photo-1574144611937-0df059b5ef3e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8ZnVubnklMjBjYXR8ZW58MHx8MHx8fDA%3D&auto=format&fit=crop&w=500&q=60',
            'https://images.unsplash.com/photo-1561948955-570b270e7c36?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2101&q=80']
    },
    'default': {
        'text': 'what else?',
        'images': []
    }
}


class ChatEndpoint(Resource):
    def post(self):
        payload = request.get_json()
        chat_invocation_logger.info(json.dumps(payload, indent=1))
        query = payload['query']

        if query in response_map:
            result = response_map[query]
        else:
            result = response_map['default']
        return jsonify(result)


app = Flask(__name__)
CORS(app)
api = Api(app)

api.add_resource(ChatEndpoint, '/verifast')



@app.route('/store_data', methods=['POST'])
def store_data():
    try:
        # Get the JSON payload from the frontend
        payload = request.json

        # Insert the payload into the MongoDB collection
        inserted_document = collection.insert_one(payload)

        if inserted_document.inserted_id:
            response = {"message": "Data stored successfully", "document_id": str(inserted_document.inserted_id)}
            return jsonify(response), 201  # Respond with HTTP status code 201 (Created)
        else:
            return jsonify({"message": "Failed to store data"}), 500  # Respond with HTTP status code 500 (Internal Server Error)

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 400  # Respond with HTTP status code 400 (Bad Request)


if __name__ == '__main__':
    app.run(debug=True)  # Set debug to False in a production environment
