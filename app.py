import streamlit as st
from streamlit_folium import st_folium
import folium # for map
from datetime import datetime
import requests
from streamlit_mic_recorder import mic_recorder
import streamlit.components.v1 as components
import base64

# --- Branding & Config ---
st.set_page_config(page_title="LegacyTree", layout="wide", page_icon="🌲")

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

bg_image = 'background.jpg'  # Update path if needed
bg_ext = 'jpg'       # or 'jpeg', 'png', etc.

bg_base64 = get_base64_of_bin_file(bg_image)

st.markdown(
    f"""
    <style>
    .stApp {{
        position: relative;
        min-height: 100vh;
        background-image: url('data:image/{bg_ext};base64,{bg_base64}');
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
    }}
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.6); /* Adjust the 0.5 for more/less fade */
        z-index: 0;
        pointer-events: none;
    }}
    .stApp > * {{
        position: relative;
        z-index: 1;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

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
    
    # Format date properly
    date_str = story.get('date', 'Unknown')
    if date_str and date_str != 'Unknown':
        try:
            # Handle both string dates and datetime objects
            if isinstance(date_str, str):
                if 'T' in date_str:
                    # Parse ISO format date
                    from datetime import datetime
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    formatted_date = date_obj.strftime('%Y-%m-%d')
                else:
                    formatted_date = date_str
            else:
                formatted_date = date_str
        except:
            formatted_date = date_str
    else:
        formatted_date = 'Unknown'
    
    st.markdown(f"**Theme:** `{story['theme']}` | **Date:** {formatted_date}")
    st.markdown(f"**Location:** {story['location']}")
    st.write(story['summary'])
    if story.get('message_to_future'):
        st.markdown(f"**Message to Future Generations:** _{story['message_to_future']}_")
    st.markdown(f"**Visibility:** {story.get('visibility', 'Public')}")
    if story.get('audio'):
        st.audio(story['audio'], format='audio/wav')
    if story.get('image'):
        st.image(story['image'], caption="Artifact")
    if story.get('illustration_url'):
        st.image(story['illustration_url'], caption="AI Illustration")
    st.markdown("---")

# --- Header ---
st.title("🌲 LegacyTree")
st.subheader("Where memories become roots.")
st.markdown("""
LegacyTree is your family's personal time capsule — a platform that helps elders and loved ones record their life stories, map them to the places they happened, and preserve them forever.

Using AI, we turn conversations into beautifully summarized chapters, illustrated memories, and interactive maps that can be shared across generations. Whether it's a story of migration, love, resilience, or tradition — LegacyTree ensures it's never forgotten.
""")

# --- Sidebar Navigation ---

# Custom CSS for sidebar and radio buttons
st.markdown(
    """
    <style>
    /* Sidebar background and padding */
    section[data-testid="stSidebar"] {
        background: rgba(30, 30, 30, 0.85);
        border-radius: 18px;
        margin: 16px 8px 16px 0;
        padding: 24px 12px 24px 12px;
        box-shadow: 0 4px 24px 0 rgba(0,0,0,0.25);
    }
    /* Sidebar header/logo */
    [data-testid="stSidebar"] img {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    /* Radio label styling */
    div[data-baseweb="radio"] label {
        font-size: 1.1em;
        color: #fff;
        background: rgba(34,139,34,0.15);
        border-radius: 10px;
        padding: 8px 16px;
        margin-bottom: 8px;
        transition: background 0.2s, color 0.2s;
    }
    /* Selected radio option */
    div[data-baseweb="radio"] label[data-selected="true"] {
        background: linear-gradient(90deg, #228B22 60%, #6B8E23 100%);
        color: #fff;
        font-weight: bold;
        box-shadow: 0 2px 8px 0 rgba(34,139,34,0.15);
    }
    /* Radio hover effect */
    div[data-baseweb="radio"] label:hover {
        background: rgba(34,139,34,0.35);
        color: #fff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

tab = st.sidebar.radio(
    "Navigate",
    ["Record Story", "Memory Map", "Guided Story Chat"],
    format_func=lambda x: {
        "Record Story": "🎙️ Record Story",
        "Memory Map": "🌍 Memory Map",
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
    date = st.date_input(
        "Date of memory", 
        value=datetime(1950, 1, 1),
        min_value=datetime(1900, 1, 1),
        max_value=datetime.today()
    )

    # --- New: Upload a message to future generations ---
    message_to_future = st.text_area("Message to future generations (optional)")

    # --- New: Visibility options ---
    visibility = st.radio("Who can see this story?", ["Private (Family Only)", "Public"], horizontal=True)

    # --- New: AI Illustration Generator ---
    generate_illustration = st.checkbox("Generate an AI illustration for this story")
    illustration_url = None

    if generate_illustration and transcript:
        with st.spinner("🎨 Generating AI illustration..."):
            try:
                # Call the backend to generate illustration
                response = requests.post(
                    "http://localhost:8000/api/generate-illustration",
                    json={"text": transcript},  # No style sent
                    timeout=120  # Longer timeout for image generation
                )
                
                if response.status_code == 200:
                    result = response.json()
                    illustration_url = result["illustration_url"]
                    st.success("✅ AI illustration generated!")
                    st.image(illustration_url, caption=f"AI-generated illustration")
                else:
                    st.error(f"Failed to generate illustration: {response.text}")
                    illustration_url = None
                    
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to backend for illustration generation")
                illustration_url = None
            except Exception as e:
                st.error(f"Error generating illustration: {str(e)}")
                illustration_url = None

    # --- Placeholder for AI Summarization ---
    if st.button("Summarize & Save Story"):
        if not transcript and not audio_file:
            st.error("Please provide either a transcript or upload an audio file.")
        else:
            with st.spinner("Processing your story..."):
                try:
                    # Use transcript or placeholder
                    story_text = transcript if transcript else "Audio story uploaded"
                    
                    # Get AI processing from backend
                    ai_response = requests.post(
                        "http://localhost:8000/api/process-story",
                        json={"text": story_text},
                        timeout=60
                    )
                    
                    if ai_response.status_code == 200:
                        ai_data = ai_response.json()
                        summary = ai_data["summary"]
                        title = ai_data["title"]
                        theme = ai_data["theme"]
                        st.success("🤖 AI processing completed!")
                    else:
                        # Fallback to simple processing
                        st.warning("AI processing failed, using simple processing")
                        if len(story_text) > 200:
                            summary = f"{story_text[:200]}..."
                        else:
                            summary = story_text
                        title = "A Special Memory"
                        theme = "family"
                    
                    # Prepare story data
                    story_data = {
                        "title": title,
                        "summary": summary,
                        "theme": theme,
                        "location": location or "Unknown",
                        "lat": 43.6532,  # Will be updated by backend geocoding
                        "lon": -79.3832,  # Will be updated by backend geocoding
                        "date": str(date),
                        "message_to_future": message_to_future,
                        "visibility": visibility,
                        "illustration_url": illustration_url
                    }
                    
                    # Save to backend API
                    response = requests.post(
                        "http://localhost:8000/api/stories",
                        json=story_data,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        saved_story = response.json()
                        st.success(f"Story saved successfully! ID: {saved_story['id']}")
                        
                        # Add to session state for immediate display
                        st.session_state['stories'].append({
                            'title': saved_story['title'],
                            'summary': saved_story['summary'],
                            'theme': saved_story['theme'],
                            'location': saved_story['location'],
                            'lat': saved_story['lat'],
                            'lon': saved_story['lon'],
                            'audio': audio_file.read() if audio_file else None,
                            'image': image_file,
                            'date': saved_story['date'],
                            'message_to_future': saved_story.get('message_to_future'),
                            'visibility': saved_story.get('visibility', 'Public'),
                            'illustration_url': saved_story.get('illustration_url'),
                        })
                        
                        # Clear the form
                        st.rerun()
                    else:
                        st.error(f"Failed to save story: {response.text}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to backend API. Please make sure the backend is running on http://localhost:8000")
                except Exception as e:
                    st.error(f"Error saving story: {str(e)}")

    st.markdown("---")
    st.markdown("#### Your Stories")
    for story in reversed(st.session_state['stories']):
        display_story_card(story)

# --- Memory Map Tab ---
elif tab == "Memory Map":
    st.header("🌍 Memory Map")
    st.markdown("Explore stories pinned to places. Click a pin to view the memory.")
    
    # Load stories from backend
    try:
        response = requests.get("http://localhost:8000/api/stories", timeout=10)
        if response.status_code == 200:
            backend_stories = response.json()
            # Update session state with backend data
            st.session_state['stories'] = backend_stories
            st.success(f"✅ Loaded {len(backend_stories)} stories from backend")
        else:
            st.warning("Could not load stories from backend, using local data.")
    except Exception as e:
        st.warning(f"Could not connect to backend: {str(e)}")
        st.info("Using local session data instead.")
    
    # Debug: Show story count
    story_count = len(st.session_state['stories'])
    st.info(f"📊 Total stories available: {story_count}")
    
    if story_count == 0:
        st.warning("No stories found. Create some stories in the 'Record Story' tab first!")
    else:
        # Center map on first story or default
        if st.session_state['stories']:
            first_story = st.session_state['stories'][0]
            center = [first_story['lat'], first_story['lon']]
            st.info(f"📍 Centering map on: {first_story['location']} ({first_story['lat']}, {first_story['lon']})")
        else:
            center = [20, 0]
            st.info("📍 No stories found, using default center")
        
        # Create the map
        m = folium.Map(location=center, zoom_start=2)
        
        # Add markers for each story
        for idx, story in enumerate(st.session_state['stories']):
            try:
                # Create popup content
                popup_html = f"""
                <div style="width: 300px;">
                    <h4><b>{story['title']}</b></h4>
                    <p><i>Theme: {story['theme']}</i></p>
                    <p>{story['summary'][:150]}...</p>
                    <p><i>📍 {story['location']}</i></p>
                    <p><i>📅 {story.get('date', 'Unknown')}</i></p>
                </div>
                """
                
                # Add marker to map
                folium.Marker(
                    [story['lat'], story['lon']],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=story['title'],
                    icon=folium.Icon(color='green', icon='book')
                ).add_to(m)
                
            except Exception as e:
                st.error(f"Error adding story {idx} to map: {str(e)}")
                st.write(f"Story data: {story}")
        
        # Display the map
        st_folium(m, width=700, height=500)
    
    st.markdown("---")
    st.markdown("#### All Stories")
    for story in reversed(st.session_state['stories']):
        display_story_card(story)

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
    
    # Language selection for speech
    if voice_mode:
        try:
            response = requests.get("http://localhost:8000/api/speech/languages", timeout=5)
            if response.status_code == 200:
                languages = response.json()
                language_options = {v: k for k, v in languages.items()}
                selected_language = st.selectbox(
                    "Select Language",
                    options=list(language_options.keys()),
                    index=0
                )
                language_code = language_options[selected_language]
            else:
                language_code = "en"
                st.warning("Could not load languages, using English")
        except:
            language_code = "en"
            st.warning("Could not connect to speech service, using English")

    # Display chat history (skip system prompt)
    for i, msg in enumerate(st.session_state["chat_history"]):
        if i % 2 == 0:
            st.markdown(f"**You:** {msg}")
        else:
            st.markdown(f"**AI:** {msg}")
            # Add TTS for AI responses
            if voice_mode:
                try:
                    tts_response = requests.post(
                        "http://localhost:8000/api/text-to-speech",
                        json={"text": msg, "language": language_code, "slow": False},
                        timeout=30
                    )
                    if tts_response.status_code == 200:
                        audio_url = tts_response.json()["audio_url"]
                        st.audio(audio_url, format="audio/mp3")
                except Exception as e:
                    st.error(f"TTS error: {str(e)}")

    # Input method based on voice mode
    if voice_mode:
        st.markdown("### 🎤 Speak your message:")
        audio = mic_recorder(key="mic_recorder", use_container_width=True)
        
        if audio:
            try:
                # Convert audio to base64
                audio_bytes = audio['bytes']
                audio_base64 = base64.b64encode(audio_bytes).decode()
                
                # Send to backend for STT
                stt_response = requests.post(
                    "http://localhost:8000/api/speech-to-text",
                    json={"audio_data": audio_base64, "language": language_code},
                    timeout=30
                )
                
                if stt_response.status_code == 200:
                    transcribed_text = stt_response.json()["text"]
                    st.success(f"🎤 Transcribed: {transcribed_text}")
                    user_input = transcribed_text
                else:
                    st.error("Failed to transcribe speech")
                    user_input = st.text_input("Or type your message here:", key="voice_fallback")
                    
            except Exception as e:
                st.error(f"Speech recognition error: {str(e)}")
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

# --- Footer ---
st.markdown("---")
st.markdown(
    "<center>LegacyTree - Where memories become roots.</center>", unsafe_allow_html=True
) 