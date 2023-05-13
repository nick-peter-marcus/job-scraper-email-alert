def main():
    # Import libraries
    import time

    # print counter 5 times every 3 seconds
    print("Initiating")

    for i in range(5):
        time.sleep(3)
        print(f'We are at count {i+1}')

    print("Finished")

if __name__ == '__main__':
    main()
    
