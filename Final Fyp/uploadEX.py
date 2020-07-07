
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate('fp-growth-test-firebase-adminsdk-h1p13-dea07cc96a.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://fp-growth-test.firebaseio.com/'})
ref = db.reference('User1_id_120_Churn')

pred = [1,0,1,0,1,1,1,0,0,0]
user_ref_1 = ref.child("Predictions")
i = 1
for x in pred:
    user_ref_1.update({
        'Prediction_' + str(i): {
            'Value':x,
        }})
    i+=1

user_ref_1 = ref.child("Feature Importance")
i = 1
for x in pred:
    user_ref_1.update({
        'Feature_' + str(i): {
            'Value':x,
        }})
    i+=1