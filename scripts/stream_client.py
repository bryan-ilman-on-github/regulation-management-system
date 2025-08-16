import requests
import json

# The URL of your streaming endpoint
url = "http://localhost:8000/api/v1/ai/stream-chat"

# The question you want to ask
payload = {
    "question": "Tell me a short story about a space explorer who finds a new planet."
}

# Set the headers
headers = {"Content-Type": "application/json", "Accept": "text/event-stream"}

try:
    # Make the POST request with stream=True
    with requests.post(url, json=payload, headers=headers, stream=True) as response:
        response.raise_for_status()  # Raise an exception for bad status codes

        print("AI Response: ")
        # Iterate over the response line by line
        for line in response.iter_lines():
            # Filter out empty lines
            if line:
                # Decode the line from bytes to a string
                decoded_line = line.decode("utf-8")

                # Check if the line is an SSE data line
                if decoded_line.startswith("data:"):
                    # Strip the "data: " prefix to get the JSON string
                    json_str = decoded_line[len("data: ") :]

                    try:
                        # Parse the JSON string
                        data = json.loads(json_str)
                        token = data.get("token", "")

                        # Print the token without a newline and flush the output
                        print(token, end="", flush=True)
                    except json.JSONDecodeError:
                        # Ignore lines that are not valid JSON
                        pass
        print()  # Print a final newline for a clean exit

except requests.RequestException as e:
    print(f"\nAn error occurred: {e}")
