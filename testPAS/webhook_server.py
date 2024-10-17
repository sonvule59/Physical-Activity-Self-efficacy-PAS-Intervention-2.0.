from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Endpoint for receiving webhook requests
@app.route('/send_sms', methods=['POST'])
def send_sms():
    try:
        # Extract data from the request
        data = request.get_json()
        recipient_number = data.get("to")
        message_body = data.get("message")

        # For example, using Twilio to send SMS
        # Replace 'YOUR_TWILIO_SID' and 'YOUR_TWILIO_AUTH_TOKEN' with your credentials
        twilio_sid = ""
        twilio_auth_token = ""
        twilio_number = ""

        if not recipient_number or not message_body:
            return jsonify({"error": "Missing 'to' or 'message'"}), 400

        # Using Twilio REST API to send SMS
        response = requests.post(
            f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json",
            data={
                "From": twilio_number,
                "To": recipient_number,
                "Body": message_body
            },
            auth=(twilio_sid, twilio_auth_token)
        )

        # Check if the message was sent successfully
        if response.status_code == 201:
            return jsonify({"success": "Message sent successfully"}), 200
        else:
            return jsonify({"error": response.text}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the server
if __name__ == '__main__':
    app.run(debug=True, port=5000)
