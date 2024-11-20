from flask import Blueprint, jsonify, request
from flask_mongoengine import MongoEngine
from mongoengine import Document, BooleanField, IntField, StringField, DateTimeField
from datetime import datetime
import os
import logging

main = Blueprint('main',__name__)

# # MongoDB Atlas configuration
# main.config["MONGODB_SETTINGS"] = {
#     "host": "mongodb+srv://lakshmanreddy458:CO4BzJ3Xo2NFEb8z@taskmaster.0ygad.mongodb.net/mydatabase?retryWrites=true&w=majority"
# }



# User schema
class User(Document):

    bank_name = StringField(required=True)
    uname = StringField(required=True)
    password = StringField(required=True)
    meta = {
        'collection': 'banks'
    }

# Item schema
class Item(Document):
    status = BooleanField(required=True)
    currency_value = IntField(required=True)
    currency_Id = StringField(required=True )
    uuid = StringField(required=True, unique=True)
    created_date = DateTimeField(required=True)
    last_scanned_date = DateTimeField(required=True)
    last_scanned_by = StringField(required=True)
    

    meta = {
        'collection': 'items'
    }

# Check the connection status
@main.route('/check_connection', methods=['GET'])
def check_connection():
    try:
        # Try to perform a simple query to check connection
        db.connection.admin.command('ping')  # MongoDB ping command
        return jsonify({"status": "success", "message": "MongoDB connection successful!"}), 200
    except Exception as e:
        logging.error(f"Error connecting to MongoDB: {e}")
        return jsonify({"status": "error", "message": f"MongoDB connection failed: {str(e)}"}), 500

@main.route('/add_note' , methods=['POST'])
def add_note():

    try:
        data = request.json.get('data')
        # print(data)
    #     data = {
    #     "status": True,
    #     "currency_value": 500,
    #     "currency_id": "ABC123",
    #     "uuid": "550e8400-e29b-41d4-a716-446655440000",
    #     "created_date": "2024-11-19 08:30:00",
    #     "last_scanned_date": "2024-11-19 08:30:00",
    #     "last_scanned_by": "RBI"
    # }
        item = Item(
            status=data['status'],
            currency_value=data['currency_value'],
            currency_Id = data['currency_id'],
            uuid= data['uuid'],
            created_date= data['created_date'],
            last_scanned_date= data['last_scanned_date'],
            last_scanned_by = data['last_scanned_by']
        )
        item.save()
        return jsonify({"status": "success", "message": "Note added successfully"}), 200
    except Exception as e:
        print(e)
        return jsonify({"status": "failed", "message": "Error adding note"}), 400

@main.route('/update_note', methods=['POST'])
def update_note():
    data = request.json.get('data')
    uuid = data['uuid']
    bank_uname = data['bank_uname']
    print(bank_uname)
    note_obj = Item.objects.get(uuid=uuid)
    print(note_obj)
    if note_obj :
        
        
        last_scanned = note_obj.last_scanned_date 

        curr = datetime.now()
        
        diff = curr - last_scanned
        diff_seconds = diff.total_seconds()
        three_months_in_seconds = 3 * 30 * 24 * 60 * 60  # 3 months in seconds
        print(diff_seconds , three_months_in_seconds)
        if  diff_seconds <= three_months_in_seconds:
            note_obj.last_scanned_date = datetime.now()
            
            note_obj.last_scanned_by = bank_uname
            note_obj.save()
            return jsonify({"status": "success", "message": "Note updated successfully"}), 200
        note_obj.status = False
        note_obj.save()
    
    return jsonify({"status": "failed", "message": "Error updating note"}), 400



# Route to add a new item history entry
# def add_history():
#     data = request.json.get('data')
#     print("Received data:", data)
    
#     try:
#         item = Item(
#             status=data['status'],
#             currency_value=data['currencyValue'],
#             currency_Id = data['currencyId'],
#             uuid= data['uuid'],
#             created_date= data['createdDate'],
#             last_scanned_date= data['lastScannedDate'],
#             last_scanned_by = data['lastScannedBy']

#         )
#         item.save()
        
#         response = {"status": "success", "message": "Item added to history"}
#     except Exception as e:
#         response = {"status": "error", "message": str(e)}
#     print(response)
#     return jsonify(response), 200

# Route to get all item history entries

@main.route("/note_data", methods=["GET"])
def get_note_data():
    try:
        # Fetch all items from the database
        items = Item.objects.all()
        
        # Transform items into a list of dictionaries
        result = [
            {
                "status": item.status,
                "currency_value": item.currency_value,
                "currency_id" : item.currency_Id,
                "uuid": item.uuid,
                "created_date": item.created_date.strftime("%Y-%m-%d %H:%M:%S") if item.created_date else None,
                "last_scanned_date": item.last_scanned_date.strftime("%Y-%m-%d %H:%M:%S") if item.last_scanned_date else None,
                "last_scanned_by" : item.last_scanned_by
            }
            for item in items
        ]
        
        # Success response
        response = {"status": "success", "data": result}
    except Exception as e:
        # Handle exceptions gracefully
        response = {"status": "error", "message": str(e)}
    
    return jsonify(response), 200




@main.route('/get_history', methods=['POST'])
def get_history():
    try:
        bank_name = request.json.get('uname')
        items = Item.objects(last_scanned_by=bank_name)
        result = []
        for item in items:
            items_list = {
                    "status": item.status,
                    "currency_value": item.currency_value,
                    "uuid": item.uuid,
                    "created_date": item.created_date,
                    "last_scanned_date": item.last_scanned_date
                }
            result.mainend(items_list)
            
        
        response = {"status": "success", "data": result}
    except Exception as e:
        response = {"status": "error", "message": str(e)}
    return jsonify(response), 200

# Helper function to check login credentials
def check(uname, password):
    user = User.objects(uname=uname, password=password).first()  # Query user in MongoDB
    print(user)
    return user is not None

# Route for user login
@main.route('/login', methods=['POST'])
def login():
    data = request.json
    print(data)
    uname = data.get('email')
    password = data.get('password')
    if check(uname, password):
        return jsonify({"message": "Login successful" }), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401


    
