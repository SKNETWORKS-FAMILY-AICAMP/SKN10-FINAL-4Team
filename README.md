# AI Influencer Platform

## Project Overview
A Django-based platform for interacting with AI-powered influencer chatbots. Users can chat with influencers, hear AI-generated voices, and experience dynamic content.

## Features
- User authentication (Google login via allauth)
- Dynamic influencer cards with images and voice
- Text-to-speech using ElevenLabs
- Audio and chat logging
- Modular Django app structure

## Setup
1. Clone the repository:
   ```sh
   git clone <your-repo-url>
   cd <project-directory>
   ```
2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up your `.env` file with the required secrets (see below).
5. Run migrations:
   ```sh
   python manage.py migrate
   ```
6. Start the development server:
   ```sh
   python manage.py runserver
   ```

## Environment Variables
Create a `.env` file in the project root with the following keys:
```
OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_key
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret
```

## Running the Project
- Visit `http://localhost:8000` in your browser.
- Log in with Google and interact with AI influencers.

## License
MIT License
