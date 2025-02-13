#  Marvin - Voice Activated Interactive Map Assistant

## Overview

Marvin is a realtime voice-controlled assistant designed to interact with a map interface. It allows users to perform actions such as zooming to locations, adding markers, finding routes, and toggling map layers using voice commands. This project integrates a web-based frontend with a Python backend to provide a seamless user experience.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup](#setup)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Deployment](#deployment)
  - [Docker](#docker)
  - [Manual Deployment](#manual-deployment)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Voice-Controlled Map Interaction:** Control map functions using voice commands.
- **Realtime Transcription:** Transcribes voice commands in realtime.
- **Location Search and Zoom:** Zooms into specified locations on the map.
- **Marker Placement:** Adds markers to the map based on voice commands.
- **Route Finding:** Calculates and displays routes between two locations.
- **Layer Control:** Toggles satellite and highway layers on the map.
- **Current Location:** Finds and marks the user's current location.

## Technologies Used

- **Frontend:**
  - HTML
  - CSS
  - JavaScript
  - OpenLayers
  - Axios
  - Font Awesome
- **Backend:**
  - Python 3.9
  - FastAPI
  - Transformers (Hugging Face)
  - Torch
- **Services:**
  - Nominatim (OpenStreetMap) for geocoding
  - Openrouteservice for route calculation

## Setup

### Prerequisites

Before you begin, ensure you have the following installed:

- [Python 3.9+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/get-started/) (optional, for containerized deployment)
- [pip](https://pip.pypa.io/en/stable/installing/) (Python package installer)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Mallikarjunreddy3015/hackathon.git
    cd hackathon
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  **Install the required Python packages:**

    ```bash
    pip install --no-cache-dir -r requirements.txt
    ```

## Usage

1.  **Run the FastAPI backend:**

    ```bash
    uvicorn server:app --host 127.0.0.1 --port 8080 --reload
    ```

    This command starts the server locally. The `--reload` flag enables automatic reloading upon code changes.

2.  **Open the interface in your web browser:**

    Navigate to `http://127.0.0.1:8080` to access the Realtime Assistant Interface.

3.  **Using the Interface:**

    - Ensure your microphone is enabled and accessible to the browser.
    - Wait for the "Waiting for wake word..." status.
    - Say the wake word ("Marvin") followed by your command.
    - Examples:
      - "Marvin, zoom into Australia"
      - "Marvin, Navigate me to Mumbai"
      - "Marvin, Show satellite view"

## Deployment

### Docker

1.  **Build the Docker image:**

    ```bash
    docker build -t realtime-assistant .
    ```

2.  **Run the Docker container:**

    ```bash
    docker run -d -p 8080:8080 realtime-assistant
    ```

    This command runs the container in detached mode, mapping port 8080 on the host to port 8080 in the container.

3.  **Access the application:**

    Open your web browser and go to `http://localhost:8080`.

### Manual Deployment

1.  **Install system dependencies:**

    Ensure `ffmpeg` is installed on your deployment environment.

    ```bash
    sudo apt-get update
    sudo apt-get install ffmpeg
    ```

2.  **Transfer the project files:**

    Copy all project files to your deployment server.

3.  **Set up the environment:**

    Create a virtual environment and install the dependencies as described in the [Installation](#installation) section.

4.  **Run the application:**

    ```bash
    uvicorn server:app --host 0.0.0.0 --port 8080
    ```

    This makes the application accessible from any IP address. Consider using a process manager like `systemd` or `supervisor` to ensure the application restarts automatically if it crashes.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.
