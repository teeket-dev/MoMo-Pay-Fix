from collection import Collection

momo_payment = Collection()
response = momo_payment.requestToPay(10, "0555448855", "1233")
print("request to pay: ", response, "\n")

if response["status_code"] == 202:
    response = momo_payment.getTransactionStatus(response["ref"])
    print("transaction status: ", response, "\n")

response = momo_payment.getBalance()
print("account balance: ", response, "\n")
