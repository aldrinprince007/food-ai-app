import streamlit as st
import requests

# ================= CONFIG =================
st.set_page_config(page_title="Food Finder Pro", layout="wide")

# ================= STYLING =================
st.markdown("""
<style>
.card {
    background-color: #ffffff;
    padding: 10px;
    border-radius: 15px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
.title {
    font-size: 22px;
    font-weight: bold;
}
.sub {
    color: gray;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.title("🍔 Food Finder Pro")
st.write("Find the best food near you 🍕")

# ================= INPUT =================
col1, col2 = st.columns([2,1])

with col1:
    location = st.text_input("📍 Location", "Chennai")

with col2:
    food = st.text_input("🍽️ Food", "biryani")

# ================= FUNCTIONS =================
def get_restaurants(city):
    # Step 1: Get lat/lon using Nominatim
    geo_url = f"https://nominatim.openstreetmap.org/search?format=json&q={city}"

    headers = {"User-Agent": "food-app"}

    geo_res = requests.get(geo_url, headers=headers).json()

    if not geo_res:
        return []

    lat = geo_res[0]["lat"]
    lon = geo_res[0]["lon"]

    # Step 2: Overpass query using radius
    overpass_url = "https://overpass-api.de/api/interpreter"

    query = f"""
    [out:json];
    (
      node["amenity"="restaurant"](around:3000,{lat},{lon});
      node["amenity"="fast_food"](around:3000,{lat},{lon});
    );
    out;
    """

    response = requests.post(overpass_url, data=query)

    if response.status_code == 200:
        data = response.json()
        return data.get("elements", [])
    else:
        return []
def get_food_image(food):
    return f"https://source.unsplash.com/600x400/?{food},food"

# ================= MAIN =================
if st.button("🔍 Search"):
    data = get_restaurants(location)

    if data:
        st.subheader("🔥 Top Picks Near You")

        cols = st.columns(3)

        for i, place in enumerate(data[:9]):
            with cols[i % 3]:
                name = place.get("tags", {}).get("name", "Restaurant")
                lat = place.get("lat") or place.get("center", {}).get("lat")
				lon = place.get("lon") or place.get("center", {}).get("lon")

                st.markdown('<div class="card">', unsafe_allow_html=True)

                # Image
                st.image(get_food_image(food), use_column_width=True)

                # Details
                st.markdown(f'<div class="title">🍴 {name[:40]}...</div>', unsafe_allow_html=True)
                st.markdown('<div class="sub">⭐ 4.0 • 30 mins</div>', unsafe_allow_html=True)

                # Buttons
                colA, colB = st.columns(2)

                with colA:
                    st.markdown(f"[📍 Map](https://www.google.com/maps?q={lat},{lon})")

                with colB:
                    st.markdown("[🍔 Order](https://www.swiggy.com)")

                st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.error("No restaurants found 😢")

# ================= FOOTER =================
st.write("---")
st.caption("🚀 Swiggy Style UI v4")
