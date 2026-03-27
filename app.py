import streamlit as st
import requests
from streamlit_js_eval import streamlit_js_eval

# ================= CONFIG =================
st.set_page_config(page_title="Food Finder Pro", layout="wide")

# ================= STYLING =================
st.markdown("""
<style>
.card {
    background-color: #ffffff;
    padding: 12px;
    border-radius: 15px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
.title {
    font-size: 20px;
    font-weight: bold;
}
.sub {
    color: gray;
}
</style>
""", unsafe_allow_html=True)

# ================= LOGO =================
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("logo.png", width=140)

# ================= HEADER =================
st.title("🍔 Food Finder Pro")
st.write("Find the best food near you 🍕")

# ================= INPUT =================
col1, col2 = st.columns([2,1])

with col1:
    location = st.text_input("📍 Enter Location", "Edayarpalayam, Coimbatore")

with col2:
    food = st.text_input("🍽️ What do you want?", "biryani")

# ================= LOCATION BUTTON =================
st.write("### 📍 Location Options")
use_current = st.button("📍 Use My Current Location")

if use_current:
    coords = streamlit_js_eval(js_expressions='navigator.geolocation.getCurrentPosition((pos) => pos.coords)')
    
    if coords:
        lat = coords["latitude"]
        lon = coords["longitude"]
        location = f"{lat},{lon}"
        st.success("Using your current location 📍")

# ================= FUNCTIONS =================

def get_restaurants(city, food):
    headers = {"User-Agent": "food-app"}

    # Handle coordinates OR text location
    if "," in city:
        lat, lon = city.split(",")
    else:
        geo_url = f"https://nominatim.openstreetmap.org/search?format=json&q={city}"
        geo_res = requests.get(geo_url, headers=headers).json()

        if not geo_res:
            return []

        lat = geo_res[0]["lat"]
        lon = geo_res[0]["lon"]

    # Overpass API
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

        response = requests.post(overpass_url, data=query, timeout=10)

        if response.status_code == 200:
            data = response.json().get("elements", [])
        else:
            data = []

    except:
        data = []

    # 🔥 SMART FILTER
    filtered = []
    for place in data:
        tags = place.get("tags", {})
        name = tags.get("name", "").lower()
        cuisine = tags.get("cuisine", "").lower()

        if food.lower() in name or food.lower() in cuisine:
            filtered.append(place)

    if not filtered:
        filtered = data

    return filtered


def get_food_image(food):
    return f"https://source.unsplash.com/600x400/?{food},food"

# ================= MAIN =================
if st.button("🔍 Search"):
    data = get_restaurants(location, food)

    if data:
        st.subheader("🔥 Top Picks Near You")

        num_results = st.slider("Show restaurants", 5, 50, 20)

        cols = st.columns(3)

        for i, place in enumerate(data[:num_results]):
            with cols[i % 3]:

                # Handle name
                name = place.get("tags", {}).get("name", "Restaurant")

                # Handle lat/lon safely
                lat = place.get("lat") or place.get("center", {}).get("lat")
                lon = place.get("lon") or place.get("center", {}).get("lon")

                st.markdown('<div class="card">', unsafe_allow_html=True)

                st.image(get_food_image(food), use_column_width=True)

                st.markdown(f'<div class="title">🍴 {name}</div>', unsafe_allow_html=True)
                st.markdown('<div class="sub">⭐ 4.0 • 30 mins</div>', unsafe_allow_html=True)

                colA, colB = st.columns(2)

                with colA:
                    if lat and lon:
                        st.markdown(f"[📍 Map](https://www.google.com/maps?q={lat},{lon})")

                with colB:
                    st.markdown("[🍔 Order](https://www.swiggy.com)")

                st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.error("No restaurants found 😢")

# ================= FOOTER =================
st.write("---")
st.caption("🚀 Food Finder Pro vFinal")