# Tidal Music Library

A web application to view and transfer your Tidal music favorites (tracks, albums, artists, videos, playlists) between multiple Tidal accounts.

## Setup

### Prerequisites
- Python 3.8+
- pip

### Running the Application
1. Clone this repository:
   ```sh
   git clone https://github.com/yourusername/tidal-mig.git
   cd tidal-mig
   ```
2. Create a virtual environment:
   ```sh
   python -m venv .venv  # Creates a virtual environment in the .venv directory
   ```
   
3. Activate your virtual environment (if not already activated):
   ```sh
   # On Windows:
   source .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```
4. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
5. Run the app:
   ```sh
   python app.py
   ```
6. Open your browser to `http://127.0.0.1:5000`

## Usage
- **Sign in** with your Tidal account(s).
- **Switch accounts** using the dropdown in the header.
- **Transfer favorites**: Click "Transfer Favorites", select a source account and categories, and transfer.

## License
This project is licensed under the GNU GPL v3. See LICENSE for details.
