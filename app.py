import streamlit as st
from openai import OpenAI

# ========== SETUP ==========
st.set_page_config(page_title="🍔 AI Food Finder", layout="centered")

st.title("🍔 AI Food Deal Finder")
st.write("Compare Swiggy, Zomato & Blinkit using AI 🚀")

# ========== USER INPUT ==========
food_query = st.text_input("What do you want to eat?")
budget = st.slider("Select your budget (₹)", 50, 500, 200)

# ========== SAMPLE DATA ==========
food_data = [
    {"name": "Chicken Biryani", "price": 180, "rating": 4.2, "app": "Swiggy", "offer": "10% OFF"},
    {"name": "Chicken Biryani", "price": 160, "rating": 4.0, "app": "Zomato", "offer": "20% OFF"},
    {"name": "Chicken Biryani", "price": 200, "rating": 4.5, "app": "Blinkit", "offer": "Free Delivery"},
    {"name": "Veg Pizza", "price": 150, "rating": 4.1, "app": "Swiggy", "offer": "15% OFF"},
    {"name": "Veg Pizza", "price": 140, "rating": 3.9, "app": "Zomato", "offer": "25% OFF"},
]

# ========== AI LOGIC ==========
def find_best_option(food_items):
    for item in food_items:
        item["score"] = item["rating"] + (budget - item["price"]) / 100
    sorted_items = sorted(food_items, key=lambda x: x["score"], reverse=True)
    return sorted_items

# ========== FILTER DATA ==========
if food_query:
    filtered = [item for item in food_data if food_query.lower() in item["name"].lower() and item["price"] <= budget]

    if filtered:
        results = find_best_option(filtered)

        st.subheader("🔍 Results")

        for item in results:
            st.write(f"📱 {item['app']} | 🍛 {item['name']} | ⭐ {item['rating']} | 💰 ₹{item['price']} | 🎁 {item['offer']}")

        best = results[0]

        st.success(f"🏆 Best Option: {best['app']} - ₹{best['price']} ({best['offer']}) ⭐ {best['rating']}")

        # ========== AI EXPLANATION ==========
        try:
            import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": f"Why is {best['app']} the best choice for {food_query} under ₹{budget}?"
                    }
                ]
            )

            st.info("🧠 AI Recommendation:")
            st.write(response.choices[0].message.content)

        except:
            st.warning("Add your OpenAI API key to enable AI suggestions.")

    else:
        st.error("No matching food found under your budget 😢")
import os
st.write("API Key Loaded:", os.getenv("OPENAI_API_KEY") is not None)
# ========== FOOTER ==========
st.write("---")
st.caption("Made with ❤️ using AI")
