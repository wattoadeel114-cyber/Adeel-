import pandas as pd
import gradio as gr
import matplotlib.pyplot as plt
from pathlib import Path

DATA_FILE = Path(__file__).with_name("coffee_etl_output.csv")

def load_data():
    if DATA_FILE.exists():
        data = pd.read_csv(DATA_FILE)
    else:
        data = pd.DataFrame({
            "coffee": ["Black Coffee", "Espresso", "Latte",
                       "Cappuccino", "Mocha", "Americano"],
            "calories": [2, 5, 120, 80, 200, 5],
            "protein_g": [0.3, 0.1, 6, 4, 7, 0.3],
            "fat_g": [0, 0.2, 6, 4, 8, 0],
            "carbs_g": [0, 0, 9, 6, 25, 1]
        })

    data.columns = data.columns.str.strip().str.lower()
    required = ["coffee", "calories", "protein_g", "fat_g", "carbs_g"]

    if not set(required).issubset(data.columns):
        raise ValueError("The CSV is missing required columns.")

    data["coffee"] = data["coffee"].astype("string").str.strip()

    for col in required[1:]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.dropna(subset=required)
    data = data[data["coffee"].ne("")]
    data = data[(data[required[1:]] >= 0).all(axis=1)]

    if data.empty:
        raise ValueError("No valid coffee data was found.")

    return data.reset_index(drop=True)

df = load_data()
coffee_names = sorted(df["coffee"].unique().tolist())

def show_nutrition(coffee_name, servings):
    if not coffee_name or coffee_name not in coffee_names:
        return "Please select a coffee.", pd.DataFrame(), None

    servings = float(servings or 1)
    if not 0.5 <= servings <= 20:
        return "Choose between 0.5 and 20 servings.", pd.DataFrame(), None

    row = df[df["coffee"] == coffee_name].iloc[0]
    calories = float(row["calories"]) * servings
    protein = float(row["protein_g"]) * servings
    fat = float(row["fat_g"]) * servings
    carbs = float(row["carbs_g"]) * servings

    message = f"""
# ☕ {coffee_name}

**Servings:** {servings:g}

- **Calories:** {calories:.1f} kcal
- **Protein:** {protein:.1f} g
- **Fat:** {fat:.1f} g
- **Carbohydrates:** {carbs:.1f} g

*Nutrition estimates depend on your dataset and recipe.*
"""

    table = pd.DataFrame({
        "Nutrient": ["Calories (kcal)", "Protein (g)", "Fat (g)", "Carbs (g)"],
        "Amount": [calories, protein, fat, carbs]
    })

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(["Protein", "Fat", "Carbs"], [protein, fat, carbs])
    ax.set_ylabel("Grams per selected servings")
    ax.set_title(f"Nutrients in {coffee_name}")
    fig.tight_layout()

    return message, table, fig

with gr.Blocks(theme=gr.themes.Soft()) as app:
    gr.Markdown("# ☕ Coffee Nutrition App\nExplore coffee calories and nutrients.")

    coffee = gr.Dropdown(
        choices=coffee_names,
        value=coffee_names[0],
        label="Select coffee"
    )
    servings = gr.Number(value=1, label="Number of servings",
                         minimum=0.5, maximum=20)

    button = gr.Button("Show Nutrition", variant="primary")
    result = gr.Markdown()
    table = gr.Dataframe(label="Nutrition breakdown")
    chart = gr.Plot(label="Nutrient chart")

    button.click(
        show_nutrition,
        inputs=[coffee, servings],
        outputs=[result, table, chart]
    )

    app.load(
        show_nutrition,
        inputs=[coffee, servings],
        outputs=[result, table, chart]
    )

if __name__ == "__main__":
    app.launch()
