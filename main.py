import os
from dotenv import load_dotenv
from twilio.rest import Client
import time


def init_twilio_client():
    print("Initializing Twilio client...")
    load_dotenv()
    account_sid = os.getenv("MS_TWILIO_ACCOUNT_SID")
    api_sid = os.getenv("MS_TWILIO_API_KEY_SID")
    api_secret = os.getenv("MS_TWILIO_SECRET")
    service_sid = os.getenv("MS_TWILIO_DEFAULT_SERVICE_SID")
    client = Client(api_sid, api_secret, account_sid)
    return client.conversations.v1.services(service_sid)


def delete_all_conversations(service):
    for conversation in service.conversations.list():
        conversation.delete()


def get_my_conversation(service, address):
    for conversation in service.conversations.list():
        participants = conversation.participants.list()
        for participant in participants:
            if participant.messaging_binding and participant.messaging_binding["address"] == address:
                return conversation
    return None


def create_my_conversation(service, address, ms_address):
    conversation = service.conversations.create(friendly_name=f"Conversation with {address}")
    conversation.participants.create(messaging_binding_address=address, messaging_binding_proxy_address=ms_address)
    return conversation


def wait_for_user_message(conversation, address):
    while True:
        messages = conversation.messages.list()
        if len(messages) > 0 and messages[-1].author == address:
            print("Got a message from the user")
            return messages[-1].body
        print("Waiting for user message...")
        time.sleep(2)  # Wait for 2 seconds before checking again


def send_message(conversation, message):
    print(f"Sending message to the user: {message}")
    conversation.messages.create(body=message)


def main():
    service = init_twilio_client()
    address = f"whatsapp:{os.getenv('PHONE_NUMBER')}"
    ms_address = f"whatsapp:{os.getenv('MS_WHATSAPP_NUMBER')}"

    my_conversation = get_my_conversation(service, address) or create_my_conversation(service, address, ms_address)

    while True:
        user_message = wait_for_user_message(my_conversation, address)
        send_message(my_conversation,
                     f"Hey there, got your message: {user_message}, --> Length of your last message: {len(user_message)}")


if __name__ == "__main__":
    main()