import requests
import json
import uuid
from basicauth import encode
from decouple import config


class Collection:
    def __init__(self):
        self.collections_primary_key = config('COLLECTIONS_SUBKEY')
        self.api_key_collections = config('COLLECTION_API_SECRET')
        self.collections_apiuser = config('COLLECTION_USER_ID')
        self.environment_mode = config('MTN_ENVIRONMENT_MODE')
        self.callback_url = config('MTN_CALLBACK_URL')
        self.base_url = 'https://proxy.momoapi.mtn.com'

        if self.environment_mode == "sandbox":
            self.base_url = "https://sandbox.momodeveloper.mtn.com"

        # Generate Basic authorization key when in test mode
        if self.environment_mode == "sandbox":
            self.collections_apiuser = str(uuid.uuid4())

        # Create API user
        self.url = ""+str(self.base_url)+"/v1_0/apiuser"
        payload = json.dumps({
            "providerCallbackHost": 'URL of host ie google.com'
        })
        self.headers = {
            'X-Reference-Id': self.collections_apiuser,
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': self.collections_primary_key
        }
        response = requests.request(
            "POST", self.url, headers=self.headers, data=payload)

        # Create API key
        self.url = ""+str(self.base_url)+"/v1_0/apiuser/" + \
            str(self.collections_apiuser)+"/apikey"
        payload = {}
        self.headers = {
            'Ocp-Apim-Subscription-Key': self.collections_primary_key
        }
        response = requests.request(
            "POST", self.url, headers=self.headers, data=payload)
        response = response.json()

        # Auto-generate when in test mode
        if self.environment_mode == "sandbox":
            self.api_key_collections = str(response["apiKey"])

        # Create basic key for Collections
        self.username, self.password = self.collections_apiuser, self.api_key_collections
        self.basic_authorisation_collections = str(
            encode(self.username, self.password))

    def authToken(self):
        url = ""+str(self.base_url)+"/collection/token/"
        payload = {}
        headers = {
            'Ocp-Apim-Subscription-Key': self.collections_primary_key,
            'Authorization': str(self.basic_authorisation_collections)
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        authorization_token = response.json()
        return authorization_token

    def requestToPay(self, amount, phone_number, external_id, payernote="SPARCO", payermessage="SPARCOPAY", currency="EUR"):
        uuidgen = str(uuid.uuid4())
        url = ""+str(self.base_url)+"/collection/v1_0/requesttopay"
        payload = json.dumps({
            "amount": amount,
            "currency": currency,
            "externalId": external_id,
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": phone_number
            },
            "payerMessage": payermessage,
            "payeeNote": payernote
        })
        headers = {
            'X-Reference-Id': uuidgen,
            'X-Target-Environment': self.environment_mode,
            # 'X-Callback-Url': self.callback_url,
            'Ocp-Apim-Subscription-Key': self.collections_primary_key,
            'Content-Type': 'application/json',
            'Authorization': "Bearer "+str(self.authToken()["access_token"])
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        context = {"status_code": response.status_code, "ref": uuidgen}
        return context

    def getTransactionStatus(self, txn):
        url = ""+str(self.base_url)+"/collection/v1_0/requesttopay/"+str(txn)
        payload = {}
        headers = {
            'Ocp-Apim-Subscription-Key': self.collections_primary_key,
            'Authorization': "Bearer "+str(self.authToken()["access_token"]),
            'X-Target-Environment': self.environment_mode,
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        json_respon = response.json()
        return json_respon

    # Check momo collections balance
    def getBalance(self):
        url = ""+str(self.base_url)+"/collection/v1_0/account/balance"
        payload = {}
        headers = {
            'Ocp-Apim-Subscription-Key': self.collections_primary_key,
            'Authorization':  "Bearer "+str(self.authToken()["access_token"]),
            'X-Target-Environment': self.environment_mode,
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        json_respon = response.json()
        return json_respon