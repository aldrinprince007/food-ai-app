import streamlit as st
import os
from openai import OpenAI
# ================== PAGE SETUP ==================
st.set_page_config(page_title="🍔 AI Food Finder", layout="centered")

st.title("🍔 Smart Food Deal Finder")
st.write("Find best food deals across Swiggy, Zomato & Blinkit 🚀")

# ================== USER INPUT ==================
food_query = st.text_input("What do you want to eat?")
budget = st.slider("Select your budget (₹)", 50, 500, 200)

# ================== SAMPLE DATA ==================
food_data = [
    {"name": "Chicken Biryani", "price": 180, "rating": 4.2, "app": "Swiggy", "offer": "10% OFF"},
    {"name": "Chicken Biryani", "price": 160, "rating": 4.0, "app": "Zomato", "offer": "20% OFF"},
    {"name": "Chicken Biryani", "price": 200, "rating": 4.5, "app": "Blinkit", "offer": "Free Delivery"},
    
    {"name": "Veg Biryani", "price": 140, "rating": 4.1, "app": "Swiggy", "offer": "15% OFF"},
    {"name": "Veg Biryani", "price": 130, "rating": 3.9, "app": "Zomato", "offer": "25% OFF"},
    
    {"name": "Pizza", "price": 150, "rating": 4.1, "app": "Swiggy", "offer": "15% OFF"},
    {"name": "Pizza", "price": 140, "rating": 3.9, "app": "Zomato", "offer": "25% OFF"},
    
    {"name": "Burger", "price": 120, "rating": 4.0, "app": "Swiggy", "offer": "10% OFF"},
    {"name": "Burger", "price": 110, "rating": 3.8, "app": "Zomato", "offer": "20% OFF"},
]

# ================== SMART LOGIC ==================
def find_best_option(food_items):
    for item in food_items:
        item["score"] = item["rating"] + (budget - item["price"]) / 100
    return sorted(food_items, key=lambda x: x["score"], reverse=True)

# ================== FAKE AI FUNCTION (FREE) ==================
def smart_recommendation(best, food_query, budget):
    reasons = []

    # Price logic
    if best["price"] < budget:
        reasons.append("fits well within your budget 💰")

    # Rating logic
    if best["rating"] >= 4.2:
        reasons.append("has excellent ratings ⭐")

    # Offer logic
    if "OFF" in best["offer"]:
        reasons.append("gives a great discount 🎉")
    elif "Free" in best["offer"]:
        reasons.append("offers free delivery 🚚")

    # Final message
    return f"{best['app']} is the best choice for {food_query} because it {', '.join(reasons)}."

# ================== MAIN ==================
if food_query:
    filtered = []

    for item in food_data:
        if food_query.lower() in item["name"].lower():
            if item["price"] <= budget:
                filtered.append(item)

    if filtered:
        results = find_best_option(filtered)

        st.subheader("🔍 Results")

        for item in results:
            st.write(f"📱 {item['app']} | 🍛 {item['name']} | ⭐ {item['rating']} | 💰 ₹{item['price']} | 🎁 {item['offer']}")

        best = results[0]

        st.success(f"🏆 Best Option: {best['app']} - ₹{best['price']} ({best['offer']}) ⭐ {best['rating']}")

        # 🧠 FREE SMART RECOMMENDATION
        st.info("🧠 Smart Recommendation:")
        st.write(smart_recommendation(best, food_query, budget))

    else:
        st.error("No matching food found under your budget 😢")

# ================== FOOTER ==================
st.write("---")
st.caption("Made with ❤️ (No API needed)")