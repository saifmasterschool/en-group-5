import os
from dotenv import load_dotenv
from twilio.rest import Client

def init_twilio_client():
    print("Initializing Twilio client...")
    load_dotenv()
    account_sid = os.getenv("MS_TWILIO_ACCOUNT_SID")
    api_sid = os.getenv("MS_TWILIO_API_KEY_SID")
    api_secret = os.getenv("MS_TWILIO_SECRET")
    service_sid = os.getenv("MS_TWILIO_DEFAULT_SERVICE_SID")
    client = Client(api_sid, api_secret, account_sid)
    return client.conversations.v1.services(service_sid)

def create_my_conversation(service, address, ms_address):
    pass

def main():
    service = init_twilio_client()
    print(service)
    address = f"whatsapp:{os.getenv('PHONE_NUMBER')}"
    ms_address = f"whatsapp:{os.getenv('MS_WHATSAPP_NUMBER')}"

    my_conversation = create_my_conversation(service, address, ms_address)

if __name__ == "__main__":
    main()
