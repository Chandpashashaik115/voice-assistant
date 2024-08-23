import os
import azure.cognitiveservices.speech as speechsdk
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

# Load environment variables securely
headers = {
    "GOOGLE_API_KEY": st.secrets["GOOGLE_API_KEY"],
    "SPEECH_KEY": st.secrets["SPEECH_KEY"],
    "SPEECH_REGION": st.secrets["SPEECH_REGION"],
    "OPEN_AI_ENDPOINT": st.secrets["OPEN_AI_ENDPOINT"],
    "OPEN_AI_DEPLOYMENT_NAME":st.secrets["OPEN_AI_DEPLOYMENT_NAME"],
    "SUBSCRIPTION":st.secrets["SPEECH_KEY"]
}


# Configure speech recognition and synthesis using Azure Cognitive Services Speech SDK
speech_config = speechsdk.SpeechConfig(subscription=SUBSCRIPTION, region=SPEECH_REGION)
audio_output_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_config.speech_recognition_language = "en-IN"
speech_recognizer = speechsdk.SpeechRecognizer(speech_config, audio_config)
speech_config.speech_synthesis_voice_name = 'en-IN-NeerjaNeural' 
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output_config)

#speech_config.speech_synthesis_voice_name = 'en-US-JennyMultilingualNeural' 
 # Adjust voice name as needed

# Define punctuation for sentence detection
tts_sentence_end = [".", "!", "?", ";", "。", "！", "？", "；", "\n"]

# Function to synthesize speech
def speak(text):
    """Synthesizes the given text using Azure Cognitive Services Speech SDK."""
    print(f"Speech synthesized to speaker: {text}")
    speech_synthesizer.speak_text_async(text).get()

# Streamlit app
def app():
    st.title("SAGE:")
    st.header("Smart Assitant for General Engagement")

    if st.button("Terminate"):
        st.write("Conversation stopped.")
        os.kill(os.getpid(), 9)    
    

    if st.button("Start Conversation"):
        chat_with_gemini()

def chat_with_gemini():
    """Continuously listens for speech input, processes it with Gemini, and speaks responses."""
    genai.configure(api_key=GOOGLE_API_KEY)

    generation_config = {
        "temperature": 0.7,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
    }

    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    convo = model.start_chat()
    system_message = '''INSTRUCTIONS: Respond normally.
    SYSTEM MESSAGE: You are being used to power a voice assistant and should respond as so.
    As a voice assistant, respond in a maximum of two sentences. You generate only words of value, also information about movies, math calculations. Remeber the
     previous prompts to continue the conversation. Also, do not use any speacial charecters
    in the text such as * or emojis. be quiet if something asked about only cyber security and cyber crime'''

    system_message = system_message.replace(f'\n', '')
    convo.send_message(system_message)

    st.write("SAGE is listening. Say 'Stop' or press Ctrl-Z to end the conversation.")
    while True:
        try:
            # Recognize speech
            speech_recognition_result = speech_recognizer.recognize_once_async().get()

            # Handle recognized speech
            if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
                if speech_recognition_result.text.lower() == "stop":
                    st.write("Conversation ended.")
                    os.kill(os.getpid(), 9)
                    break

                # Process speech with Gemini
                user_input = speech_recognition_result.text
                st.write(f"Recognized speech: {user_input}")
                convo.send_message(user_input)

                # Generate response from Gemini
                response = convo.last.text
                st.write(f"SAGE's response: {response}")  # Print the response
                speak(response)  # Speak the generated response

            # Handle errors
            elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
                st.write("No speech could be recognized. Please try again.")
            elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = speech_recognition_result.cancellation_details
                st.write(f"Speech Recognition canceled: {cancellation_details.reason}")
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    st.write(f"Error details: {cancellation_details.error_details}")
        except Exception as e:
            st.write(f"An error occurred: {str(e)}")
            break

if __name__ == "__main__":
    app()
