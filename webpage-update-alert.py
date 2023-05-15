def main():
    # Import libraries
    import requests
    import hashlib
    import time
    from datetime import datetime

    print("Initiating")

    response = requests.get('https://nick-peter-marcus.github.io/example-webpage/').text
    hash = hashlib.sha256(response.encode('utf-8')).hexdigest()    
    
    while True:
        time.sleep(5)
        new_response = requests.get('https://nick-peter-marcus.github.io/example-webpage/').text
        new_hash = hashlib.sha256(new_response.encode('utf-8')).hexdigest()

        if new_hash == hash:
            print(f'Running... ({datetime.now():%Y-%m-%d %H:%M:%S})')
        else:
            print(f'Something has changed at {datetime.now():%Y-%m-%d %H:%M:%S}!')
        
        hash = new_hash


if __name__ == '__main__':
    main()
    
