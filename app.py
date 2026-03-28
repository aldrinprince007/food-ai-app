import streamlit as st
import requests
import folium
import random
import math
from collections import Counter
from streamlit_folium import st_folium
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="Food Finder Pro", layout="wide")

# ================= STATE =================
if "favorites" not in st.session_state:
    st.session_state.favorites = []

if "data" not in st.session_state:
    st.session_state.data = []

if "preferences" not in st.session_state:
    st.session_state.preferences = []

if "user_coords" not in st.session_state:
    st.session_state.user_coords = None

# ================= STYLING =================
st.markdown("""
<style>
.card {background:white;padding:15px;border-radius:15px;box-shadow:0 6px 15px rgba(0,0,0,0.08);}
.best {background:linear-gradient(to right,#ffcc00,#ff9900);padding:10px;border-radius:10px;}
</style>
""", unsafe_allow_html=True)

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
        data = res.json().get("elements", [])
    except:
        data = []

    keywords = food.split()
    filtered = []

    for p in data:
        tags = p.get("tags", {})
        name = tags.get("name", "").lower()
        cuisine = tags.get("cuisine", "").lower()
        if any(word in name or word in cuisine for word in keywords):
            filtered.append(p)

    return filtered if len(filtered) > 5 else data


def ai_filter(data, query):
    query = query.lower()
    keywords = query.split()
    pref = get_user_preference()

    scored = []
    for place in data:
        tags = place.get("tags", {})
        name = tags.get("name", "").lower()
        cuisine = tags.get("cuisine", "").lower()

        score = 0
        for word in keywords:
            if word in name or word in cuisine:
                score += 2

        if pref and pref in name:
            score += 2

        if "cheap" in query:
            score += 1
        if "spicy" in query:
            score += 1

        if score > 0:
            scored.append((score, place))

    scored.sort(reverse=True, key=lambda x: x[0])
    return [x[1] for x in scored]


def get_user_preference():
    if not st.session_state.preferences:
        return None
    count = Counter(st.session_state.preferences)
    return count.most_common(1)[0][0]


def explain(place, query):
    tags = place.get("tags", {})
    name = tags.get("name", "").lower()
    cuisine = tags.get("cuisine", "").lower()
    reasons = []

    for word in query.split():
        if word in name or word in cuisine:
            reasons.append(f"✔ Matches: {word}")

    if "cheap" in query:
        reasons.append("💰 Budget friendly")
    if "spicy" in query:
        reasons.append("🌶️ Spicy option")

    return reasons


def get_deal():
    return random.choice([
        "🔥 30% OFF",
        "💰 Under ₹150",
        "⚡ Free Delivery",
        "🎉 Buy 1 Get 1",
        "🔥 Flat ₹100 OFF"
    ])


def get_prices():
    return random.randint(150,350), random.randint(150,350)


def calculate_distance(lat1, lon1, lat2, lon2):
    try:
        lat1, lon1, lat2, lon2 = map(float,[lat1,lon1,lat2,lon2])
        R=6371
        dlat=math.radians(lat2-lat1)
        dlon=math.radians(lon2-lon1)
        a=(math.sin(dlat/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2)
        return round(R*(2*math.atan2(math.sqrt(a),math.sqrt(1-a))),2)
    except:
        return None


def estimate_time(distance):
    return int(distance*random.randint(8,12)) if distance else random.randint(20,40)


def calculate_score(price, distance, time):
    score=0
    if price: score+=(400-price)
    if distance: score+=(10-distance)*10
    if time: score+=(60-time)
    return score


def get_image(food):
    return f"https://source.unsplash.com/600x400/?{food},food"

# ================= NAV =================
page = st.radio("📱 Navigation", ["🏠 Home","❤️ Favorites","🗺️ Map"], horizontal=True)

# ================= HOME =================
if page == "🏠 Home":

    st.title("🍔 Food Finder Pro")

    st.markdown("🔥 Featured Partner: Hotel Deluxe Biryani (20% OFF)")
    st.markdown("📢 Ad: Get 50% OFF today!")

    location = st.text_input("📍 Location")
    food = st.text_input("🍽️ Food").lower().strip()

    if st.button("📍 Use My Location"):
        coords = streamlit_js_eval(js_expressions='navigator.geolocation.getCurrentPosition((pos)=>pos.coords)')
        if coords:
            st.session_state.user_coords=(coords['latitude'],coords['longitude'])
            location=f"{coords['latitude']},{coords['longitude']}"

    if st.button("🔍 Search"):
        if location:
            st.session_state.preferences.append(food)
            raw=get_restaurants(location,food)
            st.session_state.data=ai_filter(raw,food) or raw

    data=st.session_state.data
    pref=get_user_preference()

    if pref:
        st.write(f"🎯 Recommended for YOU: {pref}")

    if data:
        cols=st.columns(3)

        best_score=-999
        best_index=-1

        for i,p in enumerate(data[:20]):
            lat=p.get("lat") or p.get("center",{}).get("lat")
            lon=p.get("lon") or p.get("center",{}).get("lon")

            sw,zom=get_prices()
            distance=None
            time=None

            if st.session_state.user_coords and lat and lon:
                distance=calculate_distance(st.session_state.user_coords[0],st.session_state.user_coords[1],lat,lon)
                time=estimate_time(distance)

            score=calculate_score(min(sw,zom),distance or 5,time or 30)

            if score>best_score:
                best_score=score
                best_index=i

            with cols[i%3]:
                st.markdown("<div class='card'>",unsafe_allow_html=True)
                st.image(get_image(food or "food"))

                name=p.get("tags",{}).get("name","Restaurant")
                st.write(f"🍴 {name}")

                st.markdown(get_deal())

                for r in explain(p,food):
                    st.write(r)

                st.write(f"🟠 Swiggy: ₹{sw}")
                st.write(f"🔴 Zomato: ₹{zom}")

                if sw<zom:
                    st.success("Cheaper on Swiggy")
                else:
                    st.success("Cheaper on Zomato")

                if distance:
                    st.write(f"📍 {distance} km")
                    st.write(f"⏱️ {time} mins")

                if i==best_index:
                    st.markdown("🏆 BEST OVERALL DEAL")

                st.markdown("[🟠 Buy Swiggy](https://www.swiggy.com)")
                st.markdown("[🔴 Buy Zomato](https://www.zomato.com)")

                st.markdown("</div>",unsafe_allow_html=True)

    else:
        st.write("😢 No results")

# ================= FAVORITES =================
elif page == "❤️ Favorites":
    st.title("Favorites")
    for f in st.session_state.favorites:
        st.write(f)

# ================= MAP =================
elif page == "🗺️ Map":
    if st.session_state.data:
        first=st.session_state.data[0]
        lat=first.get("lat") or first.get("center",{}).get("lat")
        lon=first.get("lon") or first.get("center",{}).get("lon")
        m=folium.Map(location=[lat,lon],zoom_start=14)

        for p in st.session_state.data[:30]:
            lat=p.get("lat") or p.get("center",{}).get("lat")
            lon=p.get("lon") or p.get("center",{}).get("lon")
            name=p.get("tags",{}).get("name","Restaurant")
            if lat and lon:
                folium.Marker([lat,lon],popup=name).add_to(m)

        st_folium(m,width=800,height=500)