# app.py

import os
import re
from flask import Flask, render_template, request, send_file, make_response, flash
from ticket_generator import TicketGenerator

app = Flask(__name__)
# A secret key is required for flashing messages and session management (like cookies)
app.secret_key = 'your_super_secret_key_change_me' 

# Define the output directory for PDFs
PDF_DIR = "generated_tickets"
os.makedirs(PDF_DIR, exist_ok=True)


def sanitize_filename(name_part):
    """Removes special characters and replaces spaces with underscores."""
    if not name_part:
        return ""
    # Remove any characters that are not letters, numbers, hyphens, or spaces
    s = re.sub(r'[^a-zA-Z0-9\s-]', '', name_part)
    # Replace spaces and hyphens with a single underscore
    return re.sub(r'[\s-]+', '_', s).strip('_')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # 1. Collect data from the form
            ticket_details = {
                "passenger_name": request.form.get('passenger_name'),
                "date": request.form.get('date'),
                "from_location": request.form.get('from_location'),
                "to_location": request.form.get('to_location'),
                "dep_time": request.form.get('dep_time'),
                "deck": request.form.get('deck'),
                "seat_no": request.form.get('seat_no'),
                "price": request.form.get('price')
            }

            # 2. Generate dynamic filename
            name_parts = ticket_details["passenger_name"].split()
            initials = "".join([part[0] for part in name_parts if part]).upper()
            
            s_initials = sanitize_filename(initials)
            s_date = sanitize_filename(ticket_details["date"])
            s_from = sanitize_filename(ticket_details["from_location"])
            s_to = sanitize_filename(ticket_details["to_location"])

            pdf_filename = f"{s_initials}_{s_date}_{s_from}_to_{s_to}.pdf"
            pdf_filepath = os.path.join(PDF_DIR, pdf_filename)
            
            # 3. Generate the PDF
            generator = TicketGenerator(filename=pdf_filepath)
            generator.generate(ticket_details)
            
            # 4. Prepare response to send the file and set cookies
            response = make_response(send_file(pdf_filepath, as_attachment=True))
            
            # 5. Set cookies with the last used data
            response.set_cookie('last_date', ticket_details['date'])
            response.set_cookie('last_from', ticket_details['from_location'])
            response.set_cookie('last_to', ticket_details['to_location'])
            response.set_cookie('last_time', ticket_details['dep_time'])
            
            return response

        except FileNotFoundError as e:
            # Handle cases where font or icon files are missing
            print(f"ERROR: A required file was not found: {e}")
            flash(f"Server Error: A required file is missing. Please contact support. Details: {e}", "danger")
            return render_template('index.html')
        except Exception as e:
            # Handle other potential errors during PDF generation
            print(f"An unexpected error occurred: {e}")
            flash(f"An unexpected error occurred during PDF generation: {e}", "danger")
            return render_template('index.html')

    # For a GET request, just render the form page
    # The form will auto-populate from cookies in the browser via Jinja2
    return render_template('index.html')

if __name__ == '__main__':
    # Set debug=False for production
    app.run()