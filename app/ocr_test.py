import pymupdf
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

PDF_PATH = "data/Handwritten notes on Machine learning.pdf"

pdf = pymupdf.open(PDF_PATH)

page = pdf[0]

# Render at higher resolution
pix = page.get_pixmap(matrix=pymupdf.Matrix(3, 3))

# Convert PDF page to PIL image
image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

# Save original high-resolution image
image.save("page1_highres.png")

# Convert to grayscale
gray = image.convert("L")

# Increase contrast
gray = ImageEnhance.Contrast(gray).enhance(2.0)

# Sharpen
gray = gray.filter(ImageFilter.SHARPEN)

# Save processed image
gray.save("page1_processed.png")

# OCR
text = pytesseract.image_to_string(
    gray,
    config="--psm 6"
)

print("\n========== OCR RESULT ==========\n")
print(text)

pdf.close()