import streamlit as st
from huggingface_hub import InferenceClient
from datetime import datetime
import random
import pandas as pd


# -------------Page Configuration by using Streamlit----------------------

st.set_page_config(page_title="Creative Fashion Stylist", page_icon="🧥")


# ---------HUGGING FACE CLIENT. Here i'm using hugging face token and model ------------------

HF_TOKEN = st.secrets["HF_TOKEN"]

client = InferenceClient(
    model="meta-llama/Llama-3.1-8B",
    #"meta-llama/Llama-3.1-8B",
    # "meta-llama/Meta-Llama-3-8B",
    token=HF_TOKEN
)


# ------------SESSION STATE-------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------- INITIALIZER-------------- 
if "saved_looks" not in st.session_state:
    st.session_state.saved_looks = []
    

if "style_profile" not in st.session_state:
    st.session_state.style_profile = {
        "fit": None, "vibe": None, "colors": [], "budget": None, "occasion": None
    }


# ------------SIDEBAR — QUICK STYLE PROFILE-------------
st.sidebar.header("🎯 Your style profile")

st.sidebar.caption("Set preferences to personalize suggestions.")

fit = st.sidebar.selectbox("Preferred fit", ["+", "classic silhouette", "Relaxed", "Regular", "Tailored"])
vibe = st.sidebar.selectbox("Style vibe", ["+", "Aesthatic", "Minimal", "Smart casual", "Street", "Classic", "Athleisure", "Bold"])
colors = st.sidebar.multiselect("Favorite colors", ["+", "Baby Pink", "Purple", "Cream", "Off White", "Black", "White", "Blue", "Navy", "Beige", "Green", "Red", "Grey", "Pastels", "Earth tones", "Brights"])
budget = st.sidebar.selectbox("Budget per outfit", ["+", "Low", "Mid", "High"])
occasion = st.sidebar.selectbox("Occasion", ["+", "Workout", "Daily", "Work", "Date", "Party", "Travel", "Festive"])

if st.sidebar.button("Save profile"):
    st.session_state.style_profile = {
        "fit": None if fit == "—" else fit,
        "vibe": None if vibe == "—" else vibe,
        "colors": colors,
        "budget": None if budget == "—" else budget,
        "occasion": None if occasion == "—" else occasion
    }
    st.sidebar.success("Style profile saved.")


# -------------------INTERACTIVE FEATURES — OUTFIT CARDS-----------------------

def build_outfit_card(profile):
    # Simple, profile-aware template with randomized variety
    base_colors = profile.get("colors") or []
    pick_color = random.choice(base_colors) if base_colors else random.choice(["Black", "Navy", "Beige", "White"])
    vibe = profile.get("vibe") or random.choice(["Smart casual", "Minimal", "Street", "Classic"])
    fit = profile.get("fit") or random.choice(["Regular", "Tailored", "Relaxed"])
    occasion = profile.get("occasion") or random.choice(["Daily", "Work", "Date", "Party", "Travel"])

    tops = {
        "Minimal": ["solid tee", "mock-neck", "oxford shirt"],
        "Smart casual": ["linen shirt", "fine knit polo", "silky blouse"],
        "Street": ["oversized graphic tee", "hoodie", "coach jacket"],
        "Classic": ["button-down", "crewneck sweater", "cardigan"]
    }
    bottoms = {
        "Minimal": ["straight chinos", "clean denim"],
        "Smart casual": ["pleated trousers", "dark denim"],
        "Street": ["cargo pants", "relaxed denim"],
        "Classic": ["wool trousers", "mid-wash denim"],
        "Festive": ["embroidered dhoti pants", "silk churidar", "velvet trousers", "brocade palazzo", "sharara pants"],
        "Athleisure": ["performance joggers", "bike shorts","yoga leggings", "training track pants", "sweat shorts"
    ]
    }
    footwear = {
        "Daily": ["white sneakers", "loafers"],
        "Work": ["derby shoes", "block heels"],
        "Date": ["chelsea boots", "sleek sneakers"],
        "Party": ["statement heels", "chunky sneakers"],
        "Travel": ["comfortable sneakers", "slip-ons"],
        "Casual": ["sneakers", "loafers", "sandals"],
        "Formal": ["oxfords", "derby shoes", "heels"],
        "Festive": ["juttis", "mojari", "embroidered loafers", "heels"],
    }

    top = random.choice(tops[vibe])
    bottom = random.choice(bottoms[vibe])
    shoe = random.choice(footwear[occasion])

    accents = [
        "watch", "minimal necklace", "belt", "tote", "crossbody bag",
        "sunglasses", "light scarf", "cap", "subtle ring"
    ]
    accent_pick = ", ".join(random.sample(accents, k=2))

    return {
        "title": f"{vibe} • {occasion} • {fit}",
        "items": [
            f"{pick_color} {top} ({fit.lower()})",
            f"{bottom} ({fit.lower()})",
            f"{shoe}"
        ],
        "accent": accent_pick,
        "color": pick_color
    }

def render_outfit_card(card):
    st.markdown(f"**Look:** {card['title']}")
    st.markdown(f"- **Top:** {card['items'][0]}")
    st.markdown(f"- **Bottom:** {card['items'][1]}")
    st.markdown(f"- **Footwear:** {card['items'][2]}")
    st.markdown(f"- **Accents:** {card['accent']}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("⭐ Save this look", key=f"save_{card['title']}_{random.randint(1,99999)}"):
            st.session_state.saved_looks.append({
                "time": datetime.now().strftime("%d-%m-%Y %H:%M"),
                "title": card['title'],
                "items": card['items'],
                "accent": card['accent'],
                "color": card['color']
            })
            st.success("Saved to your looks.")
            
    with c2:
        st.info(f"Color anchor: {card['color']}")


# --------------CHAT — COMPANION STYLIST----------------

st.title("🧥 AI Fashion Design Generator ")
st.markdown("Tell me your mood, occasion, or a piece you want to style. I’ll suggest one polished idea and ask one question.")

# ---------Show saved looks---------
with st.expander("⭐ Saved looks"):
    if st.session_state.saved_looks:
        df = pd.DataFrame(st.session_state.saved_looks)
        for idx, row in df.iterrows():
            st.markdown(f"- **{row['time']}** — {row['title']}: {', '.join(row['items'])} | Accents: {row['accent']}")
    else:
        st.caption("No saved looks yet. Generate a look below and save your favorites.")
       

# ------------Display conversation----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --------Helper: prevent repeated messages-----------
def is_repeated_message(new_msg):
    if st.session_state.messages:
        last_msg = st.session_state.messages[-1]["content"]
        return new_msg.strip().lower() == last_msg.strip().lower()
    return False

# ---------Emotion / intent detection for tone and suggestion nudges--------
def detect_intent(text):
    t = text.lower()
    if any(k in t for k in ["interview", "meeting", "presentation", "office", "work"]):
        return "work"
    if any(k in t for k in ["date", "romantic", "dinner"]):
        return "date"
    if any(k in t for k in ["party", "club", "festival", "wedding", "reception"]):
        return "party"
    if any(k in t for k in ["travel", "flight", "train", "trip"]):
        return "travel"
    if any(k in t for k in ["casual", "daily", "everyday"]):
        return "daily"
    return "general"

def stylist_prompt(profile, user_text, intent):
    vibe = profile.get("vibe")
    fit = profile.get("fit")
    colors = ", ".join(profile.get("colors", [])) if profile.get("colors") else "neutral tones"
    budget = profile.get("budget") or "Mid"
    occasion = profile.get("occasion") or (intent if intent != "general" else "Daily")

    return f"""
You are a friendly, non-assumptive companion fashion stylist.
- Speak naturally, be concise, and avoid role labels.
- Use reflective listening: acknowledge the user's input in your own words.
- Offer ONE polished outfit idea tailored to vibe, fit, colors, budget, and occasion.
- Mention 2 accents (accessories) that elevate the look.
- Ask ONE open-ended question to let the user lead (no assumptions).
- If the user requests changes (color, vibe, fit, occasion), adapt and confirm.

Profile guide:
- Vibe: {vibe or "adaptive"}
- Fit: {fit or "adaptive"}
- Colors: {colors}
- Budget: {budget}
- Occasion: {occasion}

User says: {user_text}
"""

def generate_reply(messages, profile):
    # Build plain conversation (no role labels)
    intent = detect_intent(messages[-1]["content"]) if messages else "general"
    prompt = stylist_prompt(profile, messages[-1]["content"], intent)

    response = client.text_generation(
        prompt,
        max_new_tokens=200,
        temperature=0.7,
        stop_sequences=["\nUser", "\nAssistant"]
    )
    return response.strip()

#  ---Chat input----------
user_input = st.chat_input("Describe what you want to wear, the occasion, or a piece to style...")

if user_input and not is_repeated_message(user_input):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Styling..."):
        reply = generate_reply(st.session_state.messages, st.session_state.style_profile)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

elif user_input:
    st.warning("Try adding a detail (occasion, color, or vibe) for a fresher suggestion.")


# QUICK OUTFIT GENERATOR (cards)

st.divider()
st.subheader("🎒 Quick Generate ideas")

col1, col2, = st.columns(2)

# -----------Generate look---------------
with col1:
    if st.button("Generate look"):
        card = build_outfit_card(st.session_state.style_profile)
        render_outfit_card(card)
        st.session_state.current_look = card

with col2:
    st.caption("Tip: Set your style profile in the sidebar for more personalized looks.")