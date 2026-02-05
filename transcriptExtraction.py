
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi

def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "hi"])

        transcript = ""
        for item in transcript_text:
            transcript += " " + item["text"]

        return transcript

    except Exception as e:
        st.error(f"Error extracting transcript: {e}")
        return None
