# Google TTS Setup Guide

This guide will help you set up Google Cloud Text-to-Speech for the Celebrity Companion AI.

## Prerequisites

1. **Google Cloud Account**: You need a Google Cloud account with billing enabled
2. **Python Environment**: Make sure you have Python 3.8+ installed
3. **Dependencies**: Install the required packages

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Cloud Text-to-Speech API:
   - Go to "APIs & Services" > "Library"
   - Search for "Cloud Text-to-Speech API"
   - Click "Enable"

### 3. Create Service Account

1. Go to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Give it a name (e.g., "celebrity-ai-tts")
4. Add the "Cloud Text-to-Speech User" role
5. Create and download the JSON key file

### 4. Set Environment Variables

Create a `.env` file in your project root:

```bash
# Google AI API Key (for Gemini)
GOOGLE_API_KEY=your_gemini_api_key_here

# Google Cloud Credentials (for TTS)
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
```

**Important**: Replace `your_gemini_api_key_here` with your actual Gemini API key and `path/to/your/service-account-key.json` with the actual path to your downloaded service account key file.

### 5. Get Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Click "Get API key"
3. Create a new API key
4. Copy the key and add it to your `.env` file

## Usage

Once set up, you can run the Celebrity Companion AI:

```bash
python celebrity_companion_ai_clean.py
```

## Features

- **Celebrity Voices**: David Attenborough, Morgan Freeman, Scarlett Johansson, Peter Griffin
- **Text-to-Speech**: High-quality voice synthesis using Google Cloud TTS
- **Personality AI**: Each celebrity has unique personality and response style
- **Interactive Chat**: Switch between celebrities and have natural conversations

## Troubleshooting

### Common Issues

1. **"Google Cloud TTS not available"**
   - Check that `google-cloud-texttospeech` is installed
   - Verify your service account key path is correct
   - Ensure the Cloud Text-to-Speech API is enabled

2. **"Audio system: no audio player found"**
   - Install PulseAudio: `sudo apt-get install pulseaudio` (Ubuntu/Debian)
   - Or install ALSA: `sudo apt-get install alsa-utils`

3. **"Google Cloud TTS failed"**
   - Check your service account permissions
   - Verify billing is enabled on your Google Cloud project
   - Check the service account key file is valid

### Audio Playback

The system tries to use `paplay` (PulseAudio) first, then falls back to `aplay` (ALSA). Make sure you have at least one audio system installed.

## Cost Considerations

- **Google Cloud TTS**: Pay-per-use pricing, typically very affordable for personal use
- **Gemini API**: Pay-per-use pricing for AI responses
- **Free Tier**: Google Cloud offers free tier credits for new users

## Security Notes

- Never commit your service account key to version control
- Keep your API keys secure and private
- Consider using environment variables or secure secret management in production

## Support

If you encounter issues:
1. Check the Google Cloud Console for API usage and errors
2. Verify your service account has the correct permissions
3. Ensure all environment variables are set correctly
