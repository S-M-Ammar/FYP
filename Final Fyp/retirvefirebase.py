import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate('srs-db-firebase-adminsdk-84dh5-dfd95fb02f.json')
firebase_admin.initialize_app(cred, {'databaseURL': 'https://srs-db.firebaseio.com/'})
ref = db.reference('Fp-Growth-User-1')

user_ref_1 = ref.child('ItemChain_With_Filter_By_Overall').child('ItemChain-' + str(1))
user_ref_1.update({
                'Item' + str(22): {
                    'ItemName': 'Asta Lavista mother fucker',
                }})