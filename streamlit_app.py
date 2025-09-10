# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for the name on the order
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write("The name on your Smoothie will be:", name_on_order)

# Connect to Snowflake and fetch the fruit options
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch the list of fruits from the database
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).to_pandas()['FRUIT_NAME'].tolist()

# Multiselect widget for choosing ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

# Handle the order submission
if ingredients_list:
    # Create a comma-separated string of ingredients
    ingredients_string = ', '.join(ingredients_list)

    # Display the selected ingredients and name on order
    st.write(f"Selected Ingredients: {ingredients_string}")
    st.write(f"Name on Order: {name_on_order}")

    # Button to submit the order
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        try:
            # Use parameterized queries to avoid SQL injection
            insert_stmt = """
                INSERT INTO smoothies.public.orders(ingredients, name_on_order)
                VALUES (?, ?)
            """
            session.sql(insert_stmt, params=[ingredients_string, name_on_order]).collect()
            st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
        except Exception as e:
            st.error(f"An error occurred while placing your order: {str(e)}")
