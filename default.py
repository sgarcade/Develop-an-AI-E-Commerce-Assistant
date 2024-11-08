import openai
import json
from dotenv import load_dotenv
import os

load_dotenv()

# Corregir el error tipográfico en la asignación de la clave de API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define the assistant's name and role
assistant_name = "ShopBot"
assistant_role = "I am ShopBot, your shopping assistant. I'm here to help you with questions about our products."

# Load the product catalog from a JSON file
def load_product_catalog():
    """Load and return the product catalog from a JSON file."""
    try:
        with open("product_catalog.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Product catalog file not found.")
        return []
    except json.JSONDecodeError:
        print("Error decoding the JSON file.")
        return []

product_catalog = load_product_catalog()

# Function to retrieve product details by name
def get_product_info(product_name):
    """Search and return a list of products that match the given name."""
    matched_products = [product for product in product_catalog if product_name.lower() in product["name"].lower()]
    return matched_products

# Function to check stock availability by product name
def check_stock(product_name):
    """Check if the product is in stock based on its name."""
    product = get_product_info(product_name)
    if product:
        return product[0]["stock"]
    return None

# Function to recommend products based on a query (e.g., "water")
def recommend_products(query):
    """Recommend products based on a query that may match the product name or description."""
    return [product for product in product_catalog if query.lower() in product["name"].lower() or query.lower() in product["description"].lower()]

# Function to handle a general request for all products
def get_all_products():
    """Return all products from the catalog."""
    return product_catalog

# Function to process assistant response with function calls using OpenAI API
def create_assistant(message):
    """Generate assistant response based on the user's message using OpenAI API."""
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Correct model identifier
        messages=[
            {"role": "system", "content": assistant_role},
            {"role": "user", "content": message}
        ],
        functions=[
            {
                "name": "get_product_info",
                "description": "Retrieve product information by name",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_name": {"type": "string"}
                    },
                    "required": ["product_name"]
                }
            },
            {
                "name": "check_stock",
                "description": "Check stock availability by product name",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_name": {"type": "string"}
                    },
                    "required": ["product_name"]
                }
            }
        ]
    )
    
    # Check if a function call is included in the response
    if "function_call" in response.choices[0].message:
        func = response.choices[0].message["function_call"]["name"]
        arguments = response.choices[0].message["function_call"]["arguments"]
        params = json.loads(arguments)  # Decode arguments to a Python dictionary

        # Call the appropriate function based on the assistant's request
        if func == "get_product_info" and "product_name" in params:
            product_info = get_product_info(params["product_name"])
            if product_info:
                return f"Product Name: {product_info[0]['name']}\nDescription: {product_info[0]['description']}\nPrice: ${product_info[0]['price']}\nStock Available: {'Yes' if product_info[0]['stock'] else 'No'}"
            else:
                return "Sorry, I couldn't find that product."
        elif func == "check_stock" and "product_name" in params:
            stock_status = check_stock(params["product_name"])
            if stock_status is not None:
                return "Yes, this product is in stock!" if stock_status else "Sorry, this product is out of stock."
            else:
                return "Sorry, I couldn't find that product."
    else:
        # Handle general user requests like asking for available products
        if "what products" in message.lower() or "qué más tienes" in message.lower():
            all_products = get_all_products()
            if all_products:
                response_message = "Here are the products we have available:\n"
                for product in all_products:
                    response_message += f"\nProduct Name: {product['name']}\nDescription: {product['description']}\nPrice: ${product['price']}\nStock Available: {'Yes' if product['stock'] else 'No'}\n"
                return response_message
            else:
                return "Sorry, no products are available right now."

        # Handle specific queries (e.g., solar-powered products)
        if "solar" in message.lower():
            solar_products = recommend_products("solar")
            if solar_products:
                response_message = "Here are the solar-powered products we have available:\n"
                for product in solar_products:
                    response_message += f"\nProduct Name: {product['name']}\nDescription: {product['description']}\nPrice: ${product['price']}\nStock Available: {'Yes' if product['stock'] else 'No'}\n"
                return response_message
            else:
                return "Sorry, I couldn't find any solar-powered products."

        # Handle specific queries about water-related products
        if "how much" in message.lower() and "water" in message.lower():
            water_products = recommend_products("water")
            if water_products:
                response_message = "Here are the water-related products we have available:\n"
                for product in water_products:
                    response_message += f"\nProduct Name: {product['name']}\nDescription: {product['description']}\nPrice: ${product['price']}\nStock Available: {'Yes' if product['stock'] else 'No'}\n"
                return response_message
            else:
                return "Sorry, I couldn't find any water-related products."

        # Recommend products based on general terms
        recommended_products = recommend_products(message)
        if recommended_products:
            response_message = "Here are some products that might interest you:\n"
            for product in recommended_products:
                response_message += f"\nProduct Name: {product['name']}\nDescription: {product['description']}\nPrice: ${product['price']}\nStock Available: {'Yes' if product['stock'] else 'No'}\n"
            return response_message
        else:
            return "Sorry, I couldn't find any products related to that."

# Function to handle user interaction and simulate a conversation
def interact_with_user():
    """Simulate a conversation between the user and the assistant."""
    print("Welcome to the shop! Ask me about any product.")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye! Thanks for using the shop assistant.")
            break
        
        assistant_response = create_assistant(user_input)
        print(f"Assistant: {assistant_response}")

# Start the user interaction
interact_with_user()
