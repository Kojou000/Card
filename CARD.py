import random
import logging
import nest_asyncio  # Import nest_asyncio to handle nested event loops
import asyncio
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your bot token
TELEGRAM_TOKEN = '78504116ymwAqwTDTo_CzbtPMpSR6OA3MHe3s'

# Load cards from a JSON file
def load_cards():
    try:
        with open('cards.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # Return an empty list if the file doesn't exist
        return []

# Save the card list to a JSON file
def save_cards(cards):
    with open('cards.json', 'w') as file:
        json.dump(cards, file)

# Load the card list
CARD_LIST = load_cards()

# Command handler for "/start" command
async def start_command(update: Update, context: CallbackContext):
    welcome_message = (
        "👋 Welcome to the Credit Card Generator Bot!\n"
        "Use the /card command to get a random Github credit card.\n"
        "Use /help for a list of available commands."
    )
    await update.message.reply_text(welcome_message)

# Command handler for "/help" command
async def help_command(update: Update, context: CallbackContext):
    help_text = (
        "Here are the commands you can use:\n"
        "/start - Welcome message and instructions\n"
        "/card - Get a random Github credit card\n"
        "/list_cards - List all stored cards with their indices\n"
        "/add_card <number> <exp_month> <exp_year> <cvv> - Add a new card\n"
        "/remove_card <card_index> - Remove a card by index\n"
        "/help - List of available commands"
    )
    await update.message.reply_text(help_text)

# Command handler for "/card" command
async def card_command(update: Update, context: CallbackContext):
    if not CARD_LIST:
        await update.message.reply_text("No cards available. Please add some cards using /add_card.")
        return

    card_info = random.choice(CARD_LIST)  # Pick a random card

    # Extract card details
    card_number = card_info['number']
    expiration_month = card_info['exp_month']
    expiration_year = card_info['exp_year']
    cvv = card_info['cvv']

    # Format the card information with emojis and custom styling, and escape special characters for MarkdownV2
    formatted_card = (
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔢 *Card Number:* `{card_number[:4]} {card_number[4:8]} {card_number[8:12]} {card_number[12:]}`\n"
        f"📅 *Expiry Date:* `{expiration_month}\\|{expiration_year}`\n"  # Escape '|'
        f"🔒 *CVV:* `{cvv}`\n"
        f"💳 *CARD NAME* \\- `SPIKE`\n"  # Escape '-'
        "━━━━━━━━━━━━━━━━━━━━━━━"
    )

    await update.message.reply_text(formatted_card, parse_mode='MarkdownV2')

# Command handler for "/list_cards" command
async def list_cards(update: Update, context: CallbackContext):
    if not CARD_LIST:
        await update.message.reply_text("No cards available.")
        return

    cards_message = "📋 Here are your stored cards:\n"
    for index, card in enumerate(CARD_LIST):
        cards_message += f"{index}: {card['number'][:4]} **** **** ****\n"  # Mask the card number for security

    await update.message.reply_text(cards_message)

# Command handler for "/add_card" command
async def add_card(update: Update, context: CallbackContext):
    if len(context.args) != 4:
        await update.message.reply_text("Usage: /add_card <number> <exp_month> <exp_year> <cvv>")
        return

    card_info = {
        "number": context.args[0],
        "exp_month": context.args[1],
        "exp_year": context.args[2],
        "cvv": context.args[3]
    }

    CARD_LIST.append(card_info)
    save_cards(CARD_LIST)

    await update.message.reply_text("Card added successfully!")

# Command handler for "/remove_card" command
async def remove_card(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /remove_card <card_index>")
        return

    try:
        index = int(context.args[0])
        if 0 <= index < len(CARD_LIST):
            removed_card = CARD_LIST.pop(index)
            save_cards(CARD_LIST)
            await update.message.reply_text(f"Removed card: {removed_card['number']}")
        else:
            await update.message.reply_text("Invalid index.")
    except ValueError:
        await update.message.reply_text("Please provide a valid card index.")

# Main function to run the bot
async def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('card', card_command))
    application.add_handler(CommandHandler('list_cards', list_cards))  # Add the list_cards command handler
    application.add_handler(CommandHandler('add_card', add_card))  # Add the add_card command handler
    application.add_handler(CommandHandler('remove_card', remove_card))  # Add the remove_card command handler

    # Start the bot
    await application.run_polling()

if __name__ == '__main__':
    nest_asyncio.apply()  # Allow running asyncio.run in already running event loops
    asyncio.run(main())
