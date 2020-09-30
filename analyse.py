import json

def main():
    with open("fake_analysis_input.json") as file:
        incoming_data = json.load(file)
    
    print(incoming_data)

main()