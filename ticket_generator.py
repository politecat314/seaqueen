# ticket_generator.py

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import red, black

# --- Libraries for RTL text processing ---
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
except ImportError:
    print("Error: Required libraries not found. Please run: pip install arabic-reshaper python-bidi")
    exit()

class TicketGenerator:
    """
    A class to generate a Sea Queen ferry ticket PDF with correct RTL text rendering.
    """

    def __init__(self, filename="ferry_ticket.pdf"):
        # --- File and Font Setup ---
        self.filename = filename
        # Use relative paths that work within a Flask app structure
        self.font_path = "faruma.ttf" 
        self.icon_path = os.path.join("static", "crown.png")

        # Check for required files
        if not os.path.exists(self.font_path):
            raise FileNotFoundError(f"Font file not found at '{self.font_path}'. Please ensure 'faruma.ttf' is in the root directory of the app.")
        if not os.path.exists(self.icon_path):
            raise FileNotFoundError(f"Icon file not found at '{self.icon_path}'. Please ensure 'crown.png' is in the 'static' directory.")

        # Register the custom font for Dhivehi script
        pdfmetrics.registerFont(TTFont('Thaana', self.font_path))
        
        # --- Document Dimensions ---
        self.width = 7 * inch
        self.height = 3.5 * inch
        self.c = canvas.Canvas(self.filename, pagesize=(self.width, self.height))

    def _process_rtl_text(self, text):
        """Processes a string for correct RTL display."""
        reshaped_text = arabic_reshaper.reshape(text)
        display_text = get_display(reshaped_text)
        return display_text

    def _draw_static_elements(self):
        """Draws the static text, lines, and boxes of the ticket template."""
        # --- Title ---
        self.c.setFont("Helvetica-Bold", 20)
        self.c.drawString(0.5 * inch, 3.2 * inch, "SEA")
        self.c.drawImage(self.icon_path, 1.1 * inch, 3.2 * inch, width=0.4 * inch, height=0.25 * inch, mask='auto')
        self.c.drawString(1.6 * inch, 3.2 * inch, "QUEEN")

        # --- Right Header ---
        self.c.setFont("Helvetica-Bold", 10)
        self.c.drawRightString(6.5 * inch, 3.3 * inch, "TICKET / BOARDING PASS")
        self.c.setFont("Thaana", 10)
        processed_header = self._process_rtl_text("ޓިކެޓް / ބޯޑިންގ ޕާސް")
        self.c.drawRightString(6.5 * inch, 3.1 * inch, processed_header)

        # --- Field Labels (Left Column) ---
        y_pos = 2.7
        labels_left = [
            ("NAME OF PASSENGER", "ފަސިންޖަރުގެ ނަން"), ("DATE", "ތާރީޚް"),
            ("FROM", "ފުރިތަން"), ("TO", "ދާ ތަން")
        ]
        x_box_left_start = 2.0 * inch
        box_width_left = 1.8 * inch
        
        for eng, dhiv in labels_left:
            self.c.setFont("Helvetica", 9)
            self.c.drawString(0.5 * inch, y_pos * inch, eng)
            self.c.setFont("Thaana", 9)
            processed_dhiv = self._process_rtl_text(dhiv)
            self.c.drawRightString(x_box_left_start - 0.1 * inch, (y_pos - 0.15) * inch, processed_dhiv)
            self.c.rect(x_box_left_start, (y_pos - 0.1) * inch, box_width_left, 0.25 * inch)
            y_pos -= 0.5
        
        # --- Field Labels (Right Column) ---
        box_width_right = 1.5 * inch

        # DEP TIME
        self.c.setFont("Helvetica", 9)
        self.c.drawString(4.0 * inch, 2.7 * inch, "DEP TIME")
        self.c.setFont("Thaana", 9)
        processed_time = self._process_rtl_text("ފުރާ ގަޑި")
        self.c.drawRightString(4.6 * inch, 2.55 * inch, processed_time)
        self.c.rect(4.7 * inch, 2.6 * inch, box_width_right, 0.25 * inch)

        # DECK
        self.c.setFont("Helvetica", 9)
        self.c.drawString(4.0 * inch, 2.2 * inch, "DECK")
        self.c.setFont("Thaana", 9)
        processed_deck = self._process_rtl_text("ޑެކް")
        self.c.drawRightString(4.6 * inch, 2.05 * inch, processed_deck)
        deck_opts = [("UPPER", "މަތި"), ("MAIN", "މެދެ"), ("LOWER", "ތިރި")]
        y_pos_deck = 2.2
        for eng_deck, dhiv_deck in deck_opts:
            self.c.rect(4.7 * inch, (y_pos_deck - 0.05) * inch, 0.15 * inch, 0.15 * inch)
            self.c.setFont("Helvetica", 9)
            self.c.drawString(4.9 * inch, y_pos_deck * inch, eng_deck)
            self.c.setFont("Thaana", 9)
            processed_dhiv_deck = self._process_rtl_text(dhiv_deck)
            self.c.drawRightString(6.4 * inch, y_pos_deck * inch, processed_dhiv_deck)
            y_pos_deck -= 0.25

        # Other right fields
        y_pos = 1.3
        labels_right = [("SEAT NO", "ސީޓް ނަންބަރު"), ("PRICE", "އަގު")]
        for eng, dhiv in labels_right:
            self.c.setFont("Helvetica", 9)
            self.c.drawString(4.0 * inch, y_pos * inch, eng)
            self.c.setFont("Thaana", 9)
            processed_dhiv = self._process_rtl_text(dhiv)
            self.c.drawRightString(4.6 * inch, (y_pos - 0.15) * inch, processed_dhiv)
            self.c.rect(4.7 * inch, (y_pos - 0.1) * inch, box_width_right, 0.25 * inch)
            y_pos -= 0.5

    def _fill_data(self, data):
        """Fills the user-provided data into the template."""
        self.c.setFont("Helvetica-Bold", 10)
        
        x_fill_left = 2.05 * inch
        self.c.drawString(x_fill_left, 2.65 * inch, str(data.get("passenger_name", "")))
        self.c.drawString(x_fill_left, 2.15 * inch, str(data.get("date", "")))
        self.c.drawString(x_fill_left, 1.65 * inch, str(data.get("from_location", "")))
        self.c.drawString(x_fill_left, 1.15 * inch, str(data.get("to_location", "")))

        self.c.drawString(4.75 * inch, 2.65 * inch, str(data.get("dep_time", "")))
        self.c.drawString(4.75 * inch, 1.25 * inch, str(data.get("seat_no", "")))
        self.c.drawString(4.75 * inch, 0.75 * inch, "MVR " + str(data.get("price", "")))

        # Mark the selected deck
        deck = data.get("deck", "").upper()
        check_y = None
        if deck == "UPPER": check_y = 2.15 * inch
        elif deck == "MAIN": check_y = 1.90 * inch
        elif deck == "LOWER": check_y = 1.65 * inch
        
        if check_y:
            self.c.setFont("Helvetica-Bold", 12)
            self.c.drawString(4.72 * inch, check_y + 0.01 * inch, "✓")

    def generate(self, data):
        """Generates the ticket by drawing all elements and saving the file."""
        self._draw_static_elements()
        self._fill_data(data)
        self.c.save()