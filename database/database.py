import motor.motor_asyncio
from config import ADMINS, DB_URL, DB_NAME

dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)
database = dbclient[DB_NAME]

user_data = database['users']
admin_data = database['admins']

fsub = database['fsub']
req_db = database['req_db']

default_verify = {
    'is_verified': False,
    'verified_time': 0,
    'verify_token': "",
    'link': ""
}

def new_user(id):
    return {
        '_id': id,
        'verify_status': {
            'is_verified': False,
            'verified_time': "",
            'verify_token': "",
            'link': ""
        }
    }

# Users
async def present_user(user_id: int):
    found = await user_data.find_one({'_id': user_id})
    return bool(found)

async def add_user(user_id: int):
    user = new_user(user_id)
    await user_data.insert_one(user)
    return

async def db_verify_status(user_id):
    user = await user_data.find_one({'_id': user_id})
    if user:
        return user.get('verify_status', default_verify)
    return default_verify

async def db_update_verify_status(user_id, verify):
    await user_data.update_one({'_id': user_id}, {'$set': {'verify_status': verify}})

async def full_userbase():
    user_docs = user_data.find()
    user_ids = [doc['_id'] async for doc in user_docs]
    return user_ids

async def del_user(user_id: int):
    await user_data.delete_one({'_id': user_id})
    return

# Admins
async def present_admin(user_id: int):
    found = await admin_data.find_one({'_id': user_id})
    return bool(found)

async def add_admin(user_id: int):
    user = new_user(user_id)
    await admin_data.insert_one(user)
    ADMINS.append(int(user_id))
    return

async def del_admin(user_id: int):
    await admin_data.delete_one({'_id': user_id})
    ADMINS.remove(int(user_id))
    return

async def full_adminbase():
    user_docs = admin_data.find()
    user_ids = [int(doc['_id']) async for doc in user_docs]
    return user_ids

# Force Subscription Management
async def add_force_sub_channel(channel_id: int):
    await fsub.update_one(
        {"_id": "force_sub_channels"},
        {"$addToSet": {"channel_ids": channel_id}},
        upsert=True
    )

async def remove_force_sub_channel(channel_id: int):
    await fsub.update_one(
        {"_id": "force_sub_channels"},
        {"$pull": {"channel_ids": channel_id}}
    )

async def get_force_sub_channels():
    fsub_entry = await fsub.find_one({"_id": "force_sub_channels"})
    return fsub_entry.get("channel_ids", []) if fsub_entry else []

# Request Subscription Management
async def add_request_channel(channel_id: int):
    await req_db.update_one(
        {"_id": "request_channels"},
        {"$addToSet": {"channel_ids": channel_id}},
        upsert=True
    )

async def remove_request_channel(channel_id: int):
    await req_db.update_one(
        {"_id": "request_channels"},
        {"$pull": {"channel_ids": channel_id}}
    )

async def get_request_channels():
    req_db_entry = await req_db.find_one({"_id": "request_channels"})
    return req_db_entry.get("channel_ids", []) if req_db_entry else []

# Join Requests Tracking
async def add_join_request(channel_id: int, user_data):
    await req_db.update_one(
        {"_id": channel_id},
        {"$push": {"User_INFO": user_data}},
        upsert=True
    )
