#!/usr/bin/env python3
"""
WiFi QR Code PDF Generator - Steph Innovations S.A.
====================================================
INSTRUCCIONES: Reemplazá "Steph.3840" en la línea de abajo
por la contraseña real de tu red WiFi, y ejecutá este script.
"""
 
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageDraw, ImageFont
import io
import os
 
# ╔══════════════════════════════════════════════════════════╗
# ║  👇 CAMBIÁ ESTA LÍNEA CON TU CONTRASEÑA REAL 👇        ║
# ╠══════════════════════════════════════════════════════════╣
 
WIFI_PASSWORD = "Steph.3840"
 
# ╚══════════════════════════════════════════════════════════╝
 
WIFI_SSID = "MERCUSYS_41BE"
WIFI_SECURITY = "WPA"  # WPA/WPA2/WPA3
 
# Colors
PRIMARY_BLACK = HexColor("#1A1A1A")
ACCENT_CORAL = HexColor("#E8856C")
LIGHT_BG = HexColor("#F5F5F5")
MEDIUM_GRAY = HexColor("#888888")
DARK_GRAY = HexColor("#333333")
 
def generate_wifi_qr(ssid, password, security="WPA"):
    """Generate WiFi QR code as PIL Image"""
    wifi_string = f"WIFI:T:{security};S:{ssid};P:{password};;"
    
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=2,
    )
    qr.add_data(wifi_string)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="#1A1A1A", back_color="white").convert("RGBA")
    return qr_img
 
def draw_rounded_rect(c, x, y, width, height, radius, fill_color=None, stroke_color=None, stroke_width=1):
    """Draw a rounded rectangle on the canvas"""
    p = c.beginPath()
    p.moveTo(x + radius, y)
    p.lineTo(x + width - radius, y)
    p.arcTo(x + width - radius, y, x + width, y + radius, radius)
    p.lineTo(x + width, y + height - radius)
    p.arcTo(x + width, y + height - radius, x + width - radius, y + height, radius)
    p.lineTo(x + radius, y + height)
    p.arcTo(x + radius, y + height, x, y + height - radius, radius)
    p.lineTo(x, y + radius)
    p.arcTo(x, y + radius, x + radius, y, radius)
    p.close()
    
    if fill_color:
        c.setFillColor(fill_color)
    if stroke_color:
        c.setStrokeColor(stroke_color)
        c.setLineWidth(stroke_width)
    
    if fill_color and stroke_color:
        c.drawPath(p, fill=1, stroke=1)
    elif fill_color:
        c.drawPath(p, fill=1, stroke=0)
    elif stroke_color:
        c.drawPath(p, fill=0, stroke=1)
 
def create_pdf(output_path):
    width, height = A4
    c = canvas.Canvas(output_path, pagesize=A4)
    
    # --- BACKGROUND ---
    c.setFillColor(white)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    
    # --- MAIN CARD ---
    card_w = 160 * mm
    card_h = 230 * mm
    card_x = (width - card_w) / 2
    card_y = (height - card_h) / 2
    
    # Card shadow
    draw_rounded_rect(c, card_x + 2*mm, card_y - 2*mm, card_w, card_h, 12*mm,
                      fill_color=HexColor("#E0E0E0"))
    
    # Card background
    draw_rounded_rect(c, card_x, card_y, card_w, card_h, 12*mm,
                      fill_color=white, stroke_color=HexColor("#E8E8E8"), stroke_width=1.5)
    
    # --- TOP ACCENT BAR ---
    bar_h = 6 * mm
    bar_y = card_y + card_h - 20*mm
    # Coral accent line
    c.setFillColor(ACCENT_CORAL)
    c.rect(card_x + 30*mm, bar_y, card_w - 60*mm, 2*mm, fill=1, stroke=0)
    
    # --- LOGO ---
    logo_path = "/home/claude/logo.jpg"
    if os.path.exists(logo_path):
        logo_img = Image.open(logo_path)
        # Make logo with transparent bg (white bg removal)
        logo_w = 50 * mm
        logo_h = 50 * mm * (logo_img.height / logo_img.width)
        logo_x = (width - logo_w) / 2
        logo_y = bar_y + 8 * mm
        c.drawImage(ImageReader(logo_img), logo_x, logo_y, logo_w, logo_h,
                    preserveAspectRatio=True, mask='auto')
    
    # --- COMPANY NAME ---
    c.setFillColor(PRIMARY_BLACK)
    c.setFont("Helvetica-Bold", 11)
    company_text = "STEPH INNOVATIONS S.A."
    text_w = c.stringWidth(company_text, "Helvetica-Bold", 11)
    c.drawString((width - text_w) / 2, bar_y - 8*mm, company_text)
    
    # --- WIFI ICON LABEL ---
    c.setFont("Helvetica", 9)
    c.setFillColor(MEDIUM_GRAY)
    wifi_label = "Red WiFi de la oficina"
    label_w = c.stringWidth(wifi_label, "Helvetica", 9)
    c.drawString((width - label_w) / 2, bar_y - 16*mm, wifi_label)
    
    # --- QR CODE ---
    qr_img = generate_wifi_qr(WIFI_SSID, WIFI_PASSWORD, WIFI_SECURITY)
    
    # QR container with subtle border
    qr_size = 75 * mm
    qr_x = (width - qr_size) / 2
    qr_y = card_y + card_h/2 - qr_size/2 - 22*mm
    
    # QR background box
    qr_padding = 6 * mm
    draw_rounded_rect(c, qr_x - qr_padding, qr_y - qr_padding,
                      qr_size + 2*qr_padding, qr_size + 2*qr_padding, 6*mm,
                      fill_color=LIGHT_BG, stroke_color=HexColor("#E0E0E0"), stroke_width=0.8)
    
    # Draw QR
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    c.drawImage(ImageReader(qr_buffer), qr_x, qr_y, qr_size, qr_size,
                preserveAspectRatio=True, mask='auto')
    
    # --- "Escaneá para conectarte" text ---
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(ACCENT_CORAL)
    scan_text = "Escaneá para conectarte"
    scan_w = c.stringWidth(scan_text, "Helvetica-Bold", 10)
    c.drawString((width - scan_w) / 2, qr_y - 12*mm, scan_text)
    
    # --- WIFI DETAILS BOX ---
    details_y = qr_y - 42 * mm
    details_h = 22 * mm
    details_w = card_w - 40 * mm
    details_x = card_x + 20 * mm
    
    draw_rounded_rect(c, details_x, details_y, details_w, details_h, 4*mm,
                      fill_color=HexColor("#FAFAFA"), stroke_color=HexColor("#EEEEEE"), stroke_width=0.6)
    
    # Network name
    c.setFont("Helvetica", 8)
    c.setFillColor(MEDIUM_GRAY)
    c.drawString(details_x + 8*mm, details_y + details_h - 8*mm, "RED")
    
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(DARK_GRAY)
    c.drawString(details_x + 30*mm, details_y + details_h - 8*mm, WIFI_SSID)
    
    # Password
    c.setFont("Helvetica", 8)
    c.setFillColor(MEDIUM_GRAY)
    c.drawString(details_x + 8*mm, details_y + details_h - 17*mm, "CLAVE")
    
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(DARK_GRAY)
    display_pw = WIFI_PASSWORD if WIFI_PASSWORD != "Steph.3840" else "••••••••••"
    c.drawString(details_x + 30*mm, details_y + details_h - 17*mm, display_pw)
    
    # --- FOOTER ---
    c.setFont("Helvetica", 7)
    c.setFillColor(HexColor("#BBBBBB"))
    footer1 = "Apuntá la cámara de tu celular al código QR para conectarte automáticamente."
    f1_w = c.stringWidth(footer1, "Helvetica", 7)
    c.drawString((width - f1_w) / 2, card_y + 10*mm, footer1)
    
    # --- CORAL BOTTOM ACCENT ---
    c.setFillColor(ACCENT_CORAL)
    c.rect(card_x + 30*mm, card_y + 4*mm, card_w - 60*mm, 2*mm, fill=1, stroke=0)
    
    c.save()
    print(f"✅ PDF generado: {output_path}")
    if WIFI_PASSWORD == "Steph.3840":
        print("\n⚠️  RECORDÁ: Abrí este script, reemplazá 'Steph.3840'")
        print("   por tu contraseña real, y volvé a ejecutar:")
        print("   python3 generate_pdf.py")
 
if __name__ == "__main__":
    output = "/home/claude/wifi_steph.pdf"
    create_pdf(output)
    
    # Copy to outputs
    import shutil
    os.makedirs("/mnt/user-data/outputs", exist_ok=True)
    shutil.copy(output, "/mnt/user-data/outputs/wifi_steph.pdf")
    shutil.copy(__file__, "/mnt/user-data/outputs/generate_pdf.py")
    print("📁 Archivos copiados a outputs/")