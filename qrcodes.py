import networkx as nx
import pyttsx3
import json
import cv2

# Initialize the text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed of speech
engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)

# Set a valid voice
voices = engine.getProperty('voices')
if voices:
    engine.setProperty('voice', voices[0].id)

# Function to find the shortest path using Dijkstra's algorithm
def dijkstra(start, end, adj_matrix):
    G = nx.Graph()
    for node, edges in adj_matrix.items():
        for neighbor, weight in edges.items():
            if weight > 0:
                G.add_edge(node, neighbor, weight=weight)
    
    length, path = nx.single_source_dijkstra(G, source=start, target=end)
    return path, length

# Function to speak directions
def speak_directions(path, matrix):
    for i in range(len(path) - 1):
        current_point = path[i]
        next_point = path[i + 1]
        distance = matrix[current_point][next_point]
        direction = f"You reached {current_point}. Walk {distance} meters to {next_point}."
        print(direction)  # Debugging output
        engine.say(direction)
        engine.runAndWait()

# Function to scan QR code
def scan_qr_code(expected_location):
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()

    while True:
        ret, img = cap.read()
        if not ret:
            print("Camera error. Please check your webcam.")
            break

        data, bbox, _ = detector.detectAndDecode(img)
        if data:
            print(f"QR Code detected: {data}")
            current_location = data.strip().upper()
            if current_location == expected_location:
                print(f"Reached {current_location}")
                break

        cv2.imshow("QR Code Scanner", img)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

# Function to process scanned data
def process_scanned_data(start, end, adj_matrix):
    path, total_distance = dijkstra(start, end, adj_matrix)
    
    print(f"Shortest path: {' -> '.join(path)}")
    print(f"Total cost: {total_distance} meters")
    
    speak_directions(path, adj_matrix)

    for next_point in path[1:]:
        print(f"Scanning for {next_point}...")
        scan_qr_code(next_point)

# Load data from JSON file
try:
    with open('dj_data.json', 'r') as file:
        data = json.load(file)
        adj_matrix = data['adj_matrix']
        checkpoints = data['checkpoints']
        current_location = data['current_location']
        end_point = data['end_point']
    
    # Start navigation
    process_scanned_data(current_location, end_point, adj_matrix)

except FileNotFoundError:
    print("Error: 'dj_data.json' file not found. Please check the file location.")
except json.JSONDecodeError:
    print("Error: JSON file is not formatted correctly.")
