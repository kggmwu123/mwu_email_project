from flask import Flask, request
import telebot
from telebot import types
from dotenv import load_dotenv
import mysql.connector
import re
import os
import logging
import logging

logging.basicConfig(filename='app.log', level=logging.DEBUG)
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

load_dotenv()
db = mysql.connector.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', ''),
    database=os.getenv('DB_NAME', 'ict')
)

# Telegram Bot token
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '6943008733:AAGXq619kbAiFcLiZcHD0pBHtv7miQnA6y0')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Define the stages of the conversation
user_data = {}
FIRST_NAME, LAST_NAME, EMAIL, COLLEGE, DEPARTMENT = range(5)

# Regex for validation
email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
name_regex = r'^[a-zA-Z]+$'

# List of colleges and departments
colleges = {
    "College of Engineering": ["Civil Engineering", "Electrical Engineering", "Mechanical Engineering", "Water Engineering", "COTM", "Surveying Engineering", "Engineering Drawing and Design"],
    "College of Business and Economics": ["Accounting and Finance", "Marketing-Management", "Tourism Management", "Management", "Business Management"],
    "College of Social Science and Humanities": ["History", "Philosophy", "Civic", "English", "Afaan Oromo and Literature", "Amharic Language and Literature"],
    "College of Computing": ["Information Science", "Computer Science", "Information System", "Information Technology"],
    "College of Education and Behavioral Studies": ["Psychology", "EDPM", "Civics and Ethical Education", "Sociology", "Geography and Environmental Study", "Adult Education and Community Development"],
    "College of Health Science": ["Nursing", "Midwifery", "Medical Laboratory", "Public Health Officer", "Gynecology"],
    "College of Natural and Computational Science": ["Biology", "Chemistry", "Math", "Physics", "Environmental Science", "Sport Science", "Statistics", "GIS"],
    "College of Medicine": ["Medicine", "Pharmacy"],
    "School of Law": ["Law"],
    "College of Agriculture and Natural Science": ["Agricultural Economics", "Forestry", "Plant Science", "Biodiversity Conservation and Ecotourism", "Natural Resource Management", "Rural Development and Agricultural Extension", "Animal and Range Science"]
}

# Group chat ID
GROUP_CHAT_ID = -1002180959916

# Function to check if the user is already registered
def is_user_registered(username):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM staff WHERE username = %s", (username,))
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0
    except mysql.connector.Error as err:
        print(f"Error checking user registration: {err}")
        return False

# Define bot handlers
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}
    username = message.from_user.username

    if not username:
        bot.send_message(chat_id, "You need to set a username in your Telegram profile to register.")
        return

    user_data[chat_id]['username'] = username

    if is_user_registered(username):
        bot.send_message(chat_id, "You are already registered.")
        return

    welcome_text = (
        "Welcome to the Staff Registration Bot!\n\n"
        "This bot will guide you through the process of registering your details.\n"
        "You will be asked to provide the following information:\n"
        "1. First Name\n"
        "2. Last Name\n"
        "3. Email\n"
        "4. College\n"
        "5. Department\n\n"
        "Available commands:\n"
        "/start - Begin the registration process\n"
        "/edit - Edit your registration details\n"
        "/cancel - Cancel the current registration\n"
        "/help - Display this help message\n\n"
        "To begin, please enter your first name:"
    )
    bot.send_message(chat_id, welcome_text)
    bot.register_next_step_handler(message, get_first_name)

def get_first_name(message):
    chat_id = message.chat.id
    first_name = message.text.strip()
    if re.match(name_regex, first_name):
        user_data[chat_id]['first_name'] = first_name
        bot.send_message(chat_id, "Great! Now please enter your last name:")
        bot.register_next_step_handler(message, get_last_name)
    else:
        bot.send_message(chat_id, "Invalid name. Please enter a valid first name:")

def get_last_name(message):
    chat_id = message.chat.id
    last_name = message.text.strip()
    if re.match(name_regex, last_name):
        user_data[chat_id]['last_name'] = last_name
        bot.send_message(chat_id, "Thanks! Now please enter your email address:")
        bot.register_next_step_handler(message, get_email)
    else:
        bot.send_message(chat_id, "Invalid name. Please enter a valid last name:")

def get_email(message):
    chat_id = message.chat.id
    email = message.text.strip()
    if re.match(email_regex, email):
        user_data[chat_id]['email'] = email
        bot.send_message(chat_id, "Perfect! Now please select your college:")
        college_buttons = [types.KeyboardButton(college) for college in colleges.keys()]
        markup = types.ReplyKeyboardMarkup(row_width=1)
        markup.add(*college_buttons)
        bot.send_message(chat_id, "Select your college:", reply_markup=markup)
        bot.register_next_step_handler(message, get_college)
    else:
        bot.send_message(chat_id, "Invalid email address. Please enter a valid email:")

def get_college(message):
    chat_id = message.chat.id
    college = message.text.strip()
    if college in colleges:
        user_data[chat_id]['college'] = college
        bot.send_message(chat_id, "Excellent! Now please select your department:")
        department_buttons = [types.KeyboardButton(department) for department in colleges[college]]
        markup = types.ReplyKeyboardMarkup(row_width=1)
        markup.add(*department_buttons)
        bot.send_message(chat_id, "Select your department:", reply_markup=markup)
        bot.register_next_step_handler(message, get_department)
    else:
        bot.send_message(chat_id, "Invalid college. Please select a valid college:")

def get_department(message):
    chat_id = message.chat.id
    department = message.text.strip()
    college = user_data[chat_id].get('college')
    username = user_data[chat_id].get('username')

    if department in colleges.get(college, []):
        user_data[chat_id]['department'] = department
        first_name = user_data[chat_id]['first_name']
        last_name = user_data[chat_id]['last_name']
        email = user_data[chat_id]['email']
        college = user_data[chat_id]['college']
        department = user_data[chat_id]['department']

        confirmation_message = (
            f"Please confirm your details:\n\n"
            f"First Name: {first_name}\n"
            f"Last Name: {last_name}\n"
            f"Email: {email}\n"
            f"College: {college}\n"
            f"Department: {department}\n\n"
            "Type 'confirm' to save or 'cancel' to restart."
        )
        bot.send_message(chat_id, confirmation_message)
        bot.register_next_step_handler(message, confirm_details)
    else:
        bot.send_message(chat_id, "Invalid department. Please select a valid department:")

def confirm_details(message):
    chat_id = message.chat.id
    if message.text.strip().lower() == 'confirm':
        try:
            cursor = db.cursor()
            first_name = user_data[chat_id]['first_name']
            last_name = user_data[chat_id]['last_name']
            email = user_data[chat_id]['email']
            college = user_data[chat_id]['college']
            department = user_data[chat_id]['department']
            username = user_data[chat_id]['username']

            cursor.execute(
                "INSERT INTO staff (first_name, last_name, email, college, department, username) VALUES (%s, %s, %s, %s, %s, %s)",
                (first_name, last_name, email, college, department, username)
            )
            db.commit()
            cursor.close()
            bot.send_message(chat_id, "Thank you for registering! Your details have been saved.")

            # Send notification to the group chat
            group_message = (
                f"New registration:\n"
                f"First Name: {first_name}\n"
                f"Last Name: {last_name}\n"
                f"Email: {email}\n"
                f"College: {college}\n"
                f"Department: {department}\n"
                f"Username: @{username}"
            )
            bot.send_message(GROUP_CHAT_ID, group_message)

        except mysql.connector.Error as err:
            bot.send_message(chat_id, f"Error saving your details: {err}")
            print(f"Error saving user details: {err}")

    elif message.text.strip().lower() == 'cancel':
        bot.send_message(chat_id, "Registration process cancelled. You can start again by typing /start.")

    user_data.pop(chat_id, None)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_str = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return 'OK', 200
    else:
        return 'Unsupported Media Type', 415

if __name__ == '__main__':
    bot.polling(none_stop=True)
