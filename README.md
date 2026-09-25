# PlayOK WebSocket Chess Bot

A fully automated chess bot that connects [PlayOK](https://www.playok.com/) to a UCI chess engine through PlayOK's WebSocket protocol.

The project was built by reverse engineering the communication between the PlayOK browser client and server, then reproducing the required behavior in Python.

## What it does

- Connects to PlayOK through WebSocket
- Monitors available chess tables
- Joins games automatically
- Selects a side and starts games
- Receives opponent moves
- Maintains the chess position with `python-chess`
- Sends positions to a UCI chess engine
- Converts engine moves to PlayOK's custom move format
- Sends engine moves back to PlayOK
- Continues looking for another game after a game ends

The included example uses the **ABC chess engine**.

## Project Structure

- `config.py` — Configuration and PlayOK protocol constants
- `engine.py` — UCI engine and chess/PlayOK move conversion
- `playok.py` — PlayOK WebSocket client and game logic
- `main.py` — Console driver

## Book

The complete development process, reverse-engineering methodology, WebSocket analysis, protocol decoding, chess-engine integration, and testing are documented in the free book:

**[Read the book](PLACEHOLDER_WEBSOCKET_BOOK_LINK)**

The book is a practical programming project covering reverse engineering, WebSockets, Python, networking, threading, protocol analysis, chess programming, UCI, bit manipulation, debugging, and software architecture.

## Requirements

- Python 3
- `python-chess`
- `websocket-client`
- A UCI-compatible chess engine

## Disclaimer

This project is intended for educational purposes. It demonstrates how to inspect and reproduce WebSocket communication and how to integrate an external chess engine with an online chess client.