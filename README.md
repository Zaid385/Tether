# Tether

A modern WhatsApp/Telegram-inspired real-time messaging application using raw TCP socket programming.

## Project Structure
- `server/`: Backend logic, database interaction, and client handling.
- `client/`: PySide6 GUI and networking client.
- `shared/`: Protocol definitions, constants, and utilities used by both.
- `docs/`: Documentation and protocol specifications.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure environment variables in a `.env` file.
3. Start the server:
   ```bash
   python -m server.server
   ```
4. Start the client:
   ```bash
   python -m client.main
   ```
