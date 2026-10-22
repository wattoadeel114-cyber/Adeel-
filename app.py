import streamlit as st
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

st.set_page_config(page_title="Coffee Nutrition Predictor", page_icon="☕")
st.title("☕ Coffee Nutrition - Calorie Predictor")
st.write("Project by Adeel - EDA + Decision Tree Model")

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/wattoadeel114-cyber/Adeel-/main/cleaned_coffee_nutrition.csv"
    return pd.read_csv(url)

df = load_data()
st.subheader("Your Dataset from GitHub")
st.dataframe(df)

X = df[['serving_ml','protein_g','fat_g','carbs_g']]
y = df['calorie_category']
model = DecisionTreeClassifier()
model.fit(X, y)

st.subheader("🔮 Predict Calorie Category")
serving = st.number_input("Serving (ml)", 30, 500, 240)
protein = st.number_input("Protein (g)", 0.0, 20.0, 7.0)
fat = st.number_input("Fat (g)", 0.0, 20.0, 7.0)
carbs = st.number_input("Carbs (g)", 0.0, 50.0, 10.0)

if st.button("Predict"):
    pred = model.predict([[serving, protein, fat, carbs]])
    st.success(f"Predicted Category: {pred[0]}")

st.subheader("EDA Insights")
st.bar_chart(df.set_index('coffee')['calories'])
