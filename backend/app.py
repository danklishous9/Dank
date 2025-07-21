from flask import Flask, request, send_from_directory
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__, static_folder='../frontend')

# Your Account SID and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
account_sid = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
auth_token = "your_auth_token"
client = Client(account_sid, auth_token)

@app.route('/start', methods=['POST'])
def start_call():
    """
    Starts the process of waiting on hold.
    """
    # In a real application, you would get this from the request
    phone_number_to_call = request.json.get('phone_number')
    if not phone_number_to_call:
        return {"status": "error", "message": "phone_number is required"}, 400

    # This is the URL that Twilio will request when the call is answered.
    # We'll use ngrok to expose our local server to the internet.
    status_callback_url = "http://<your_ngrok_url>/status"

    call = client.calls.create(
                        twiml='<Response><Say>Connecting you to the next available agent.</Say><Hangup/></Response>',
                        to=phone_number_to_call,
                        from_='+15017122661', # A Twilio phone number you own
                        status_callback=status_callback_url,
                        status_callback_event=['answered', 'completed'],
                    )

    return {"status": "success", "message": f"Calling {phone_number_to_call}...", "call_sid": call.sid}

@app.route('/status', methods=['POST'])
def status():
    """
    Handles the status of the call.
    """
    call_status = request.form['CallStatus']
    call_sid = request.form['CallSid']

    print(f"Call SID: {call_sid}, Status: {call_status}")

    if call_status == 'answered':
        # Here we would start the process of detecting hold music vs a human.
        # For now, we'll just log that the call was answered.
        print("Call answered! Now listening for a human...")

    return "OK"

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
