import os
from dotenv import load_dotenv
from twilio.rest import Client
import time
from user_input import process_user_input


def init_twilio_client():
    """
    Function initializes Twilio API client (our workspace)
    by loading credentials from environment variables.
    """
    print("Initializing Twilio client...")
    # load .env file into memory
    load_dotenv()

    # os.getenv() reads/fetches Account SID (service identifier)
    account_sid = os.getenv("MS_TWILIO_ACCOUNT_SID")
    # ... fetches API Key SID (identifier for API authentication)
    api_sid = os.getenv("MS_TWILIO_API_KEY_SID")
    # ... fetches API Secret (used for security)
    api_secret = os.getenv("MS_TWILIO_SECRET")
    # unique identifier for our messaging service in Twilio ("our workspace" where all conversations happen")
    service_sid = os.getenv("MS_TWILIO_DEFAULT_SERVICE_SID")
    client = Client(api_sid, api_secret, account_sid)

    # accessing Twilio Conversations API, returning our specific messaging service
    return client.conversations.v1.services(service_sid)


def delete_all_conversations(service):
    """
    Function deletes all active conversations.
    """
    # service.conversations.list() returns list of conversations
    # where each convo represents a chat session
    for conversation in service.conversations.list():
        conversation.delete()


def get_my_conversation(service, address):
    """
    Function searches for a convo that includes a specific user.
    """
    # gets all conversations and loops through each convo
    for conversation in service.conversations.list():
        # retrieves all participants in the convo as a list
        participants = conversation.participants.list()
        for participant in participants:
            # <messaging_binding> attribute = dictionary with details how participant is connected
            # e.g. messaging platform, user phone num, Twilio num as "middleman"
            # <participant.messaging_binding> holds info how user is connected
            if participant.messaging_binding and participant.messaging_binding["address"] == address:
                return conversation

    return None


def create_my_conversation(service, address, ms_address):
    """
    Function creates a new conversation if no conversation exists.
    """
    # creates new conversation object in Twilio, basically:
    # <service> = folder, <service.conversations> = list of all chats, <create> = add a new chat to the folder
    conversation = service.conversations.create(friendly_name=f"Conversation with {address}")
    # adds a participant (user)
    conversation.participants.create(messaging_binding_address=address, messaging_binding_proxy_address=ms_address)

    return conversation


def wait_for_user_message(conversation, address):
    """
    Function waits for user to send message.
    """
    while True:
        # get all messages in the conversation as a list
        messages = conversation.messages.list()
        if len(messages) > 0 and messages[-1].author == address:
            print("Got a message from the user")
            return messages[-1].body

        print("Waiting for user message...")
        # Wait for 2 seconds before checking again
        time.sleep(2)


def send_message(conversation, message):
    """
    Function sends message back to user.
    """
    print(f"Sending message to the user: {message}")
    # creates new message and sends it to the convo
    conversation.messages.create(body=message)


def main():
    """
    Main function initializes Twilio and retrieves messaging service,
    formats the phone numbers for Twilio (that is why use of f-string),
    checks if convo exists, if not creates one,keeps waiting for messages and responding
    """
    # our Twilio messaging service (our workspace where conversations happen)
    # <service> is like a folder that hold all conversations
    service = init_twilio_client()
    address = f"whatsapp:{os.getenv('PHONE_NUMBER')}"
    ms_address = f"whatsapp:{os.getenv('MS_WHATSAPP_NUMBER')}"

    # checks if convo exists <or> (if not existing) creates a new one convo
    my_conversation = get_my_conversation(service, address) or create_my_conversation(service, address, ms_address)

    while True:
        user_message = wait_for_user_message(my_conversation, address)

        # tuple with city and time
        api_query = process_user_input(user_message)
        print(api_query)
        # location, date = api_query


        send_message(my_conversation,
                     f"Hey there, got your message: {user_message}, --> Length of your last message: {len(user_message)}")


if __name__ == "__main__":
    main()