import streamlit as st
from streamlit_folium import st_folium
import folium # for map
from datetime import datetime
import requests
from streamlit_mic_recorder import mic_recorder
import streamlit.components.v1 as components

# --- Branding & Config ---
st.set_page_config(page_title="LegacyTree", layout="wide", page_icon="🌳")

# --- Demo Data Store (in-memory for MVP) ---
# This checks if the 'stories' key is not present in Streamlit's session state.
# If it's missing, it initializes 'stories' with a default list of story dictionaries.
if 'stories' not in st.session_state:
    st.session_state['stories'] = [
        {
            'title': 'Where I Met Your Grandfather',
            'summary': 'During the war, I met your grandfather in a small village. We shared stories under the stars, and that night changed my life forever. Our love grew amidst hardship, teaching us the value of hope and resilience.\n\nYears later, we returned to that village, planting a tree to remember our beginnings. That tree still stands, a symbol of our enduring love and the roots of our family.',
            'theme': 'love',
            'location': 'Toronto, Canada',
            'lat': 43.6532,
            'lon': -79.3832,
            'audio': None,
            'image': None,
            'date': '1944-06-12',
        },
        {
            'title': 'The Great Migration',
            'summary': 'Leaving India for Canada was both exciting and terrifying. I packed only what I could carry, but brought with me a heart full of dreams.\n\nThe journey taught me about courage, faith, and the importance of family. Every challenge became a lesson, and every friend a blessing.',
            'theme': 'tradition',
            'location': 'Mumbai, India',
            'lat': 19.0760,
            'lon': 72.8777,
            'audio': None,
            'image': None,
            'date': '1962-09-01',
        },
    ]

# --- Helper Functions ---
def display_story_card(story):
    st.markdown(f"### {story['title']}")
    st.markdown(f"**Theme:** `{story['theme']}` | **Date:** {story.get('date', 'Unknown')}")
    st.markdown(f"**Location:** {story['location']}")
    st.write(story['summary'])
    if story.get('message_to_future'):
        st.markdown(f"**Message to Future Generations:** _{story['message_to_future']}_")
    st.markdown(f"**Visibility:** {story.get('visibility', 'Public')}")
    if story['audio']:
        st.audio(story['audio'], format='audio/wav')
    if story['image']:
        st.image(story['image'], caption="Artifact")
    if story.get('illustration_url'):
        st.image(story['illustration_url'], caption="AI Illustration")
    st.markdown("---")

# --- Header ---
st.title("🌳 LegacyTree")
st.subheader("Where memories become roots.")
st.markdown(
    "> _Preserve your family's stories, mapped and organized by AI.\n> \n> **LegacyTree** helps elders record, organize, and share their life stories—pinning memories to places, and letting future generations ask questions and relive the past. _"
)

# --- Sidebar Navigation ---
tab = st.sidebar.radio(
    "Navigate",
    ["Record Story", "Memory Map", "Posthumous Chat", "Guided Story Chat"],
    format_func=lambda x: {
        "Record Story": "🎙️ Record Story",
        "Memory Map": "🌍 Memory Map",
        "Posthumous Chat": "💬 Posthumous Chat",
        "Guided Story Chat": "🤖 Guided Story Chat"
    }[x]
)

# --- Record Story Tab ---
if tab == "Record Story":
    st.header("🎙️ Record a Memory")
    st.markdown("Share a story from your life. You can record your voice or upload an audio file. Optionally, add a photo or artifact.")

    # Audio upload
    audio_file = st.file_uploader("Upload an audio file (WAV/MP3)", type=["wav", "mp3"])
    # (Optional) Image upload
    image_file = st.file_uploader("Upload a photo or artifact (optional)", type=["jpg", "jpeg", "png"])

    # (Optional) Manual transcript
    transcript = st.text_area("Or paste your story transcript here:")

    # Location input
    location = st.text_input("Where did this story take place? (City, Country)")
    date = st.date_input("Date of memory", value=datetime.today())

    # --- New: Upload a message to future generations ---
    message_to_future = st.text_area("Message to future generations (optional)")

    # --- New: Visibility options ---
    visibility = st.radio("Who can see this story?", ["Private (Family Only)", "Public"], horizontal=True)

    # --- New: AI Illustration Generator (Mock) ---
    generate_illustration = st.checkbox("Generate an AI illustration for this story")
    illustration_url = None
    if generate_illustration and transcript:
        # Mock: Use a placeholder image URL
        illustration_url = "https://placehold.co/400x200?text=AI+Illustration"
        st.image(illustration_url, caption="AI-generated illustration (mock)")

    # --- Placeholder for AI Summarization ---
    if st.button("Summarize & Save Story"):
        # Mock: Use transcript or placeholder
        if transcript:
            summary = f"(AI Summary) {transcript[:200]}..."
            title = "A Special Memory"
            theme = "family"
        else:
            summary = "(AI Summary) This is a placeholder summary."
            title = "A Special Memory"
            theme = "family"
        # Mock: Geocode location (use fixed coords for demo)
        if location.lower().startswith("toronto"):
            lat, lon = 43.6532, -79.3832
        elif location.lower().startswith("mumbai"):
            lat, lon = 19.0760, 72.8777
        else:
            lat, lon = 40.7128, -74.0060  # Default: New York
        # Save story
        st.session_state['stories'].append({
            'title': title,
            'summary': summary,
            'theme': theme,
            'location': location or "Unknown",
            'lat': lat,
            'lon': lon,
            'audio': audio_file.read() if audio_file else None,
            'image': image_file,
            'date': str(date),
            'message_to_future': message_to_future,
            'visibility': visibility,
            'illustration_url': illustration_url,
        })
        st.success("Story saved and summarized!")

    st.markdown("---")
    st.markdown("#### Your Stories")
    for story in reversed(st.session_state['stories']):
        display_story_card(story)

# --- Memory Map Tab ---
elif tab == "Memory Map":
    st.header("🌍 Memory Map")
    st.markdown("Explore stories pinned to places. Click a pin to view the memory.")
    # Center map on first story or default
    if st.session_state['stories']:
        center = [st.session_state['stories'][0]['lat'], st.session_state['stories'][0]['lon']]
    else:
        center = [20, 0]
    m = folium.Map(location=center, zoom_start=2)
    for idx, story in enumerate(st.session_state['stories']):
        popup_html = f"""
        <b>{story['title']}</b><br>
        <i>{story['theme']}</i><br>
        {story['summary'][:100]}...<br>
        <i>{story['location']}</i><br>
        <i>{story.get('date', '')}</i>
        """
        folium.Marker(
            [story['lat'], story['lon']],
            popup=popup_html,
            tooltip=story['title'],
            icon=folium.Icon(color='green', icon='book')
        ).add_to(m)
    st_folium(m, width=700, height=500)
    st.markdown("---")
    st.markdown("#### All Stories")
    for story in reversed(st.session_state['stories']):
        display_story_card(story)

# --- Posthumous Chat Tab ---
elif tab == "Posthumous Chat":
    st.header("💬 Posthumous AI Chat")
    st.markdown(
        "Ask your loved one a question. The AI will answer in their voice, using their values and memories. (Demo mode)"
    )
    question = st.text_input("What would you like to ask?")
    if st.button("Ask AI") and question:
        # Mock AI response
        st.markdown(
            f"**Lila Rodrigues:** My dear, that's a wonderful question. Remember, forgiveness and kindness are the roots of our family. When I faced challenges, I always turned to faith and hard work. {question} is something I would have approached with love and patience."
        )
    st.markdown("---")
    st.markdown(
        "> _This feature uses AI to answer in the tone and spirit of your loved one, drawing on their stories and values._"
    )

# --- Guided Story Chat Tab ---
if tab == "Guided Story Chat":
    st.header("🤖 Guided Story Chat")
    st.markdown("Chat with the AI to help you record your story. The AI will guide you with questions and suggestions.")

    # System prompt (not shown in UI)
    SYSTEM_PROMPT = "You are a helpful AI that interviews people to record their life stories. Ask thoughtful, open-ended questions to help them share their memories."

    # Initialize chat history in session state (only real user/AI turns)
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Voice mode toggle
    voice_mode = st.checkbox("🎤 Voice Mode (Speak instead of type)", value=False)

    # Display chat history (skip system prompt)
    for i, msg in enumerate(st.session_state["chat_history"]):
        if i % 2 == 0:
            st.markdown(f"**You:** {msg}")
        else:
            st.markdown(f"**AI:** {msg}")
            # Add audio playback for AI responses
            if voice_mode:
                # Simple TTS using browser's speech synthesis
                st.markdown(f"""
                <script>
                function speak(text) {{
                    const utterance = new SpeechSynthesisUtterance(text);
                    utterance.rate = 0.9;
                    utterance.pitch = 1.0;
                    speechSynthesis.speak(utterance);
                }}
                speak("{msg.replace('"', '\\"')}");
                </script>
                """, unsafe_allow_html=True)
                if st.button(f"🔊 Play AI Response", key=f"play_{i}"):
                    st.markdown(f"""
                    <script>
                    speak("{msg.replace('"', '\\"')}");
                    </script>
                    """, unsafe_allow_html=True)

    # Input method based on voice mode
    if voice_mode:
        st.markdown("### 🎤 Speak your message:")
        audio = mic_recorder(key="mic_recorder", use_container_width=True)
        
        if audio:
            # For demo purposes, we'll use a placeholder for STT
            # In production, you'd use a real STT service like Google Speech-to-Text
            st.info("🎤 Voice detected! (STT processing would happen here)")
            user_input = st.text_input("Or type your message here:", key="voice_fallback")
        else:
            user_input = st.text_input("Or type your message here:", key="voice_fallback")
    else:
        user_input = st.text_input("You:", key="ai_story_input")

    col1, col2 = st.columns([1,1])
    with col1:
        send_clicked = st.button("Send", key="ai_story_send")
    with col2:
        reset_clicked = st.button("Reset chat", key="ai_story_reset")

    if send_clicked and user_input:
        # Add user message to history
        st.session_state["chat_history"].append(user_input)
        # Prepend system prompt for backend only
        history_for_backend = [SYSTEM_PROMPT] + st.session_state["chat_history"]
        try:
            response = requests.post(
                "http://localhost:8000/api/conversation",
                json={"history": history_for_backend},
                timeout=30
            )
            ai_reply = response.json()["response"]
        except Exception as e:
            ai_reply = f"[Error contacting AI backend: {e}]"
        # Add AI response to history
        st.session_state["chat_history"].append(ai_reply)
        st.rerun()

    if reset_clicked:
        st.session_state["chat_history"] = []
        st.rerun()

    # Add JavaScript for TTS
    if voice_mode:
        st.markdown("""
        <script>
        function speak(text) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.9;
            utterance.pitch = 1.0;
            speechSynthesis.speak(utterance);
        }
        </script>
        """, unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.markdown(
    "<center>Made with ❤️ for Hack404. LegacyTree: Where memories become roots.</center>", unsafe_allow_html=True
) 