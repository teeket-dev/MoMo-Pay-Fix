import requests #type:ignore
import json
import uuid
from django.core.exceptions import ImproperlyConfigured #type:ignore
from abc import ABC, abstractmethod

class MomoBase(ABC):
    product = None
    subscription_product_key = None
    api_key = None
    api_user = None
    environment_mode = None
    callback_url = None
    base_url = None

    def __init__(self):
        self.configure_credentials()
        # test credentials already statically generated and added in the env.local file
        # uncomment the below line for auto generation
        # self.setup_test_credentials()
        if not self.api_key or not self.subscription_product_key \
            or not self.api_user or not self.environment_mode or not self.callback_url or not self.product:
            raise ImproperlyConfigured("MOMO credentials not configured properly!")

    @abstractmethod
    def configure_credentials(self):
        raise ImproperlyConfigured("MOMO credentials not provided!")
    
    @property
    def basic_auth_credentials(self):
        return (self.api_user, self.api_key)
    
    def setup_test_credentials(self):
        if self.environment_mode == "sandbox":
            self.base_url = "https://sandbox.momodeveloper.mtn.com"
            self.api_user = str(uuid.uuid4())
            self.create_api_user()
            self.api_key = self.generate_api_key()["apiKey"]

    def generate_api_key(self):
        self.url = f"{self.base_url}/v1_0/apiuser/{self.api_user}/apikey/"
        payload = {}
        self.headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_product_key
        }
        response = requests.request(
            "POST", self.url, headers=self.headers, data=payload)
        if response.ok:
            return response.json()
        # raise error on api key generation failure
        raise Exception("Error generating api key, status code: {0}, error content: {1}".format(response.status_code, response.content) )

    def create_api_user(self):
        self.url = f"{self.base_url}/v1_0/apiuser"
        payload = json.dumps({
            "providerCallbackHost": 'URL of host ie google.com'
        })
        self.headers = {
            'X-Reference-Id': self.api_user,
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': self.subscription_product_key
        }
        response = requests.request("POST", self.url, headers=self.headers, data=payload)
        
        if response.ok:
            # return response.json()
            return
        # raise error on api key generation failure
        raise Exception("Error generating api user, status code: {0}, error content: {1}".format(response.status_code, response.content) )

    def get_authentication_token(self):
        url = f"{self.base_url}/{self.product}/token/"
        payload = {}
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_product_key,
        }
        response = requests.request("POST", url, auth=self.basic_auth_credentials, headers=headers, data=payload)
        return response.json()
 

    def configure_credentials(self):
        self.product = 'collection'
        self.subscription_product_key = config('COLLECTIONS_SUBKEY')
        self.api_key = config('COLLECTION_API_SECRET')
        self.api_user = config('COLLECTION_USER_ID')
        self.environment_mode = config('MTN_ENVIRONMENT_MODE')
        self.callback_url = config('MTN_CALLBACK_URL')
        self.base_url = 'https://proxy.momoapi.mtn.com' 
    
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