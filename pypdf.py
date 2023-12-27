from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Line

# This is setup to add extended cut lines to pdf's for inkwell ideas sidequest and npc series.  Specifically the 4up versions.
# The extended cut lines enable easier cutting on guillotines.


def find_page_middle(pdf_path):
    reader = PdfReader(pdf_path)
    first_page = reader.pages[0]
    width = first_page.mediabox[2]  # upper right x - lower left x
    height = first_page.mediabox[3]  # upper right y - lower left y

    # Calculate middle points
    middle_horizontal = height / 2  # Middle along Y-axis
    middle_vertical = width / 2  # Middle along X-axis

    return middle_horizontal, middle_vertical

class Card:
    card_width = 198.7
    card_height = 269.3
    left_line_indent = 8.6
    right_line_indent = 9.5
    top_line_indent = 8.4
    bottom_line_indent = 8.9

    def __init__(self, bottom_left_x: float, bottom_left_y: float, pdf_path):

        # Needed for working out line ends
        self.page_middle_horizontal, self.page_middle_vertical = find_page_middle(pdf_path)
        
        page_height = self.page_middle_horizontal * 2
        page_width = self.page_middle_vertical * 2

        # We've got card height & width, so from the starting coordinates, all dimensions can flow (assuming the same)
        self.bottom_left_x = bottom_left_x
        self.bottom_left_y = bottom_left_y

        self.top = self.bottom_left_y + self.card_height
        self.left = self.bottom_left_x
        self.right = self.bottom_left_x + self.card_width
        self.bottom = self.bottom_left_y

        # All are named side first, then left/right or top/bottom
        # to signify which line is being described
        self.top_left_start = (self.left + self.left_line_indent, self.top)
        self.top_right_start = (self.right - self.right_line_indent, self.top)
        self.left_top_start = (self.left, self.top - self.top_line_indent)
        self.left_bottom_start = (self.left, self.bottom + self.bottom_line_indent)
        self.right_top_start = (self.right, self.top - self.top_line_indent)
        self.right_bottom_start = (self.right, self.bottom + self.bottom_line_indent)
        self.bottom_left_start = (self.left + self.left_line_indent, self.bottom)
        self.bottom_right_start = (self.right - self.right_line_indent, self.bottom)

        # Check if it crosses a middle line
        # Top side
        if (self.top_left_start[1] < self.page_middle_horizontal):
            self.top_end = self.page_middle_horizontal
        else:
            self.top_end = page_height
        # Left side
        if (self.left_top_start[0] < self.page_middle_vertical):
            self.left_end = 0
        else:
            self.left_end = self.page_middle_vertical
        # Right side
        if (self.right_top_start[0] < self.page_middle_vertical):
            self.right_end = self.page_middle_vertical
        else:
            self.right_end = page_width
        # Bottom side
        if (self.bottom_left_start[1] < self.page_middle_horizontal):
            self.bottom_end = 0
        else:
            self.bottom_end = self.page_middle_horizontal
        
        self.lines = [
            [self.top_left_start, (self.left + self.left_line_indent, self.top_end)], # Top Left
            [self.top_right_start, (self.right - self.right_line_indent, self.top_end)], # Top Right
            [self.left_top_start, (self.left_end, self.top - self.top_line_indent)], # Left Top
            [self.left_bottom_start, (self.left_end, self.bottom + self.bottom_line_indent)], # Left Bottom
            [self.right_top_start, (self.right_end, self.top - self.top_line_indent)], # Right Top
            [self.right_bottom_start, (self.right_end, self.bottom + self.left_line_indent)], # Right Bottom
            [self.bottom_left_start, (self.left + self.left_line_indent, self.bottom_end)], # Bottom Left
            [self.bottom_right_start, (self.right - self.right_line_indent, self.bottom_end)], # Bottom Right
        ]

# cards = [bottom_left = Card(59.8,69.1)]

def add_extended_cut_lines(input_pdf_path, output_pdf_path, cards):
    reader = PdfReader(input_pdf_path, strict=False)  # Set strict to False
    writer = PdfWriter()

    for page_number, page in enumerate(reader.pages):
        writer.add_page(page)

        lines = []
        for card in cards:
            # Add the card's lines to the lines list
            lines.extend(card.lines)

        # Add each line as an annotation
        for line in lines:
            p1, p2 = line
            annotation = Line(
                rect=(p1[0], p1[1], p2[0], p2[1]),
                p1=p1,
                p2=p2
            )
            writer.add_annotation(page_number=page_number, annotation=annotation)

    # Write the annotated file to disk
    with open(output_pdf_path, "wb") as output_file:
        writer.write(output_file)

if __name__ == "__main__":
    # input_pdf_path = "./npcs-adventurers/npcs-adventurers-4up.pdf"
    input_pdf_path = "./Sidequests_Tavern/Sidequests Tavern-4up.pdf"

    output_pdf_path = f"{input_pdf_path.split('/')[2]}_extended_cut_lines.pdf"

    # Create Card instances
    cards = [
        Card(59.8, 452.9, input_pdf_path), # Top Left
        Card(352.8,452.9, input_pdf_path), # Top Right
        Card(59.8, 69.1, input_pdf_path), # Bottom Left
        Card(352.8,69.1,input_pdf_path), # Bottom Right
    ]

    # Call the function with the list of cards
    add_extended_cut_lines(input_pdf_path, output_pdf_path, cards)
