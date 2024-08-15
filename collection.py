import requests #type:ignore
import json
import uuid
from momo_base import MomoBase 

class Collection(MomoBase):
    def configure_credentials(self):
        self.product = 'collection'
        # self.subscription_product_key = config('COLLECTIONS_SUBKEY')
        # self.api_key = config('COLLECTION_API_SECRET')
        # self.api_user = config('COLLECTION_USER_ID')
        # self.environment_mode = config('MTN_ENVIRONMENT_MODE')
        # self.callback_url = config('MTN_CALLBACK_URL')

        # remove the below code when adding to the teeket main repo

        import environ # type:ignore
        import os 
        env = environ.Env()
        env_file = os.path.join('', ".env.local")
        if os.path.isfile(env_file):
            env.read_env(env_file)

        self.subscription_product_key = os.environ.get('MTN_COLLECTION_KEY', None)
        self.api_key =  os.environ.get('MTN_COLLECTION_API_KEY', None)
        self.api_user =  os.environ.get('MTN_COLLECTION_API_USER', None)
        self.environment_mode =  os.environ.get('MTN_ENVIRONMENT', None)
        self.callback_url =  os.environ.get('MTN_CALLBACK_URL', None)
        self.base_url = 'https://sandbox.momodeveloper.mtn.com'

        # end here
    
    def get_headers(self):
        return {
            'X-Target-Environment': self.environment_mode,
            # 'X-Callback-Url': self.callback_url,
            'Ocp-Apim-Subscription-Key': self.subscription_product_key,
            'Content-Type': 'application/json',
            'Authorization': "Bearer "+str(self.get_authentication_token()["access_token"])
        }
    
    def requestToPay(self, amount, phone_number, external_id, payernote="SPARCO", payermessage="SPARCOPAY", currency="EUR"):
        reference_id = str(uuid.uuid4())
        url = f"{self.base_url}/{self.product}/v1_0/requesttopay"
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
        headers = self.get_headers()
        headers.update({
            'X-Reference-Id': reference_id,
        })
        response = requests.request("POST", url, headers=headers, data=payload)
        context = {"status_code": response.status_code, "ref": reference_id}
        return context
    
    def getTransactionStatus(self, txn):
        url = f"{self.base_url}/{self.product}/v1_0/requesttopay/"+str(txn)
        payload = {}
        headers = self.get_headers()
        response = requests.request("GET", url, headers=headers, data=payload)
        json_respon = response.json()
        return json_respon
    
    def getBalance(self):
        url = f"{self.base_url}/{self.product}/v1_0/account/balance"
        payload = {}
        headers = self.get_headers()
        response = requests.request("GET", url, headers=headers, data=payload)
        json_respon = response.json()
        return json_respon
    