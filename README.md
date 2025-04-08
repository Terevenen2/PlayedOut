# PlayedOut

PlayedOut is an automatic League of Legends game recorder designed for quick game reviews. It leverages OBS (Open Broadcaster Software) to automatically start and stop game recordings and uses FFMPEG to add chapters to the resulting video files for easier navigation of key moments.

## Overview

- **Automatic Recording:** Detects when a game begins and ends using the League of Legends live game API.  
- **Event Chaptering:** Chapters are added to the recording (currently marking events, such as kills, where you are involved).  
- **Background Automation:** Manages launching OBS in the background and handles recording without manual intervention.  
- **Built-in Installers:** Contains a basic OBS installer (under development) and plans for an automated FFMPEG installer.

## Prerequisites

Before running PlayedOut, ensure you have the following installed on your system:

- **OBS Studio**  
  - Download from [obsproject.com](https://obsproject.com/)  
  - **Setup:** Create a scene tailored for capturing your League of Legends game window.
  - **OBS WebSocket:** Enable via `Tools > WebSocket Server Settings` in OBS.
- **FFMPEG**  
  - Download from [ffmpeg.org](https://ffmpeg.org/)
- **Python 3**  
  - Download from [python.org](https://www.python.org/)

## Installation

Clone the repository, install the required Python packages, and run the application:

```bash
git clone https://github.com/Terevenen2/PlayedOut
cd PlayedOut
pip install -r requirements.txt
python main.py
