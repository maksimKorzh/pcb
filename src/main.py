from playok import PlayOK

if __name__ == "__main__":
    #websocket.enableTrace(True)
    socket = PlayOK()

    socket.connect()

    while socket.running:
        message = input("> ")

        if message.lower() == "quit":
            socket.close()
            break

        socket.send_message(message)