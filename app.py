import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import streamlit_js_eval

# ================= CONFIG =================
st.set_page_config(page_title="Food Finder Pro", layout="wide")

# ================= STATE =================
if "favorites" not in st.session_state:
    st.session_state.favorites = []

if "data" not in st.session_state:
    st.session_state.data = []

# ================= STYLING =================
st.markdown("""
<style>
body {
    background-color: #f5f5f5;
}
.card {
    background: white;
    padding: 15px;
    border-radius: 15px;
    box-shadow: 0 6px 15px rgba(0,0,0,0.08);
    transition: 0.2s;
}
.card:hover {
    transform: scale(1.02);
}
.title {
    font-size: 18px;
    font-weight: bold;
}
.best {
    background: linear-gradient(to right, #ffcc00, #ff9900);
    padding: 10px;
    border-radius: 10px;
    font-weight: bold;
}
.empty {
    text-align: center;
    color: gray;
    font-size: 18px;
}
</style>
""", unsafe_allow_html=True)

# ================= NAVIGATION =================
page = st.radio("📱 Navigation", ["🏠 Home", "❤️ Favorites", "🗺️ Map"], horizontal=True)

# ================= FUNCTIONS =================

def get_restaurants(city, food):
    headers = {"User-Agent": "food-app"}

    if not city:
        return []

    if "," in city:
        lat, lon = city.split(",")
    else:
        geo_url = f"https://nominatim.openstreetmap.org/search?format=json&q={city}"
        geo_res = requests.get(geo_url, headers=headers).json()

        if not geo_res:
            return []

        lat = geo_res[0]["lat"]
        lon = geo_res[0]["lon"]

    try:
        overpass_url = "https://overpass-api.de/api/interpreter"

        query = f"""
        [out:json];
        (
          node["amenity"="restaurant"](around:5000,{lat},{lon});
          node["amenity"="fast_food"](around:5000,{lat},{lon});
        );
        out;
        """

        res = requests.post(overpass_url, data=query, timeout=10)
        data = res.json().get("elements", []) if res.status_code == 200 else []

    except:
        data = []

    # 🔥 AI-style keyword filtering
    keywords = food.split()
    filtered = []

    for p in data:
        tags = p.get("tags", {})
        name = tags.get("name", "").lower()
        cuisine = tags.get("cuisine", "").lower()

        if any(word in name or word in cuisine for word in keywords):
            filtered.append(p)

    if len(filtered) < 5:
        filtered = data

    return filtered


def ai_filter(data, query):
    query = query.lower()
    keywords = query.split()

    scored = []

    for place in data:
        tags = place.get("tags", {})
        name = tags.get("name", "").lower()
        cuisine = tags.get("cuisine", "").lower()

        score = 0

        for word in keywords:
            if word in name or word in cuisine:
                score += 2

        if "cheap" in query:
            score += 1
        if "spicy" in query:
            score += 1

        if score > 0:
            scored.append((score, place))

    scored.sort(reverse=True, key=lambda x: x[0])

    return [x[1] for x in scored]


def get_image(food):
    return f"https://source.unsplash.com/600x400/?{food},food"

# ================= HOME =================
if page == "🏠 Home":

    st.title("🍔 Food Finder Pro")

    # 🔥 Trending
    st.subheader("🔥 Trending Now")

    col1, col2, col3, col4 = st.columns(4)

    selected_food = ""

    if col1.button("🍛 Biryani"):
        selected_food = "biryani"
    if col2.button("🍕 Pizza"):
        selected_food = "pizza"
    if col3.button("🍔 Burger"):
        selected_food = "burger"
    if col4.button("🥗 Veg"):
        selected_food = "veg"

    # INPUT
    col1, col2 = st.columns([2,1])

    with col1:
        location = st.text_input("📍 Enter Location")

    with col2:
        food = st.text_input("🍽️ Food", selected_food if selected_food else "").lower().strip()

    if food == "":
        food = "food"

    # LOCATION BUTTON
    if st.button("📍 Use My Location"):
        coords = streamlit_js_eval(js_expressions='navigator.geolocation.getCurrentPosition((pos) => pos.coords)')
        if coords:
            location = f"{coords['latitude']},{coords['longitude']}"
            st.success("Using current location")

    # SEARCH
    if st.button("🔍 Search"):
        if not location:
            st.warning("📍 Please enter a location first")
        else:
            with st.spinner("🔎 Searching best food near you..."):
                raw = get_restaurants(location, food)
                st.session_state.data = ai_filter(raw, food)

    data = st.session_state.data

    if data:
        st.markdown(f"<div class='best'>🔥 Best Match for '{food.title()}'</div>", unsafe_allow_html=True)

        cols = st.columns(3)

        for i, place in enumerate(data[:20]):
            with cols[i % 3]:

                name = place.get("tags", {}).get("name", "Restaurant")
                lat = place.get("lat") or place.get("center", {}).get("lat")
                lon = place.get("lon") or place.get("center", {}).get("lon")

                st.markdown("<div class='card'>", unsafe_allow_html=True)

                st.image(get_image(food))

                st.markdown(f"<div class='title'>🍴 {name}</div>", unsafe_allow_html=True)
                st.markdown("💰 Budget • ⚡ Fast • ⭐ Popular")

                if st.button("❤️ Save", key=f"fav{i}"):
                    if name not in st.session_state.favorites:
                        st.session_state.favorites.append(name)

                if lat and lon:
                    st.markdown(f"[📍 View on Map](https://www.google.com/maps?q={lat},{lon})")

                st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown("<div class='empty'>😢 No food found<br>Try another location or dish</div>", unsafe_allow_html=True)

# ================= FAVORITES =================
elif page == "❤️ Favorites":

    st.title("❤️ Your Favorites")

    if st.session_state.favorites:
        for fav in st.session_state.favorites:
            st.write(f"🍴 {fav}")
    else:
        st.write("No favorites yet")

# ================= MAP =================
elif page == "🗺️ Map":

    st.title("🗺️ Restaurant Map")

    data = st.session_state.data

    if data:
        first = data[0]
        lat = first.get("lat") or first.get("center", {}).get("lat")
        lon = first.get("lon") or first.get("center", {}).get("lon")

        m = folium.Map(location=[lat, lon], zoom_start=14)

        for p in data[:30]:
            name = p.get("tags", {}).get("name", "Restaurant")
            lat = p.get("lat") or p.get("center", {}).get("lat")
            lon = p.get("lon") or p.get("center", {}).get("lon")

            if lat and lon:
                folium.Marker([lat, lon], popup=name).add_to(m)

        st_folium(m, width=800, height=500)

    else:
        st.info("Search something first on Home page")