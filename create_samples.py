from reportlab.pdfgen import canvas
import os

def create_sample_pdf(filename, content):
    folder = r"C:\Proyectos\Aventi\Fichas Tecnicas"
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    path = os.path.join(folder, filename)
    c = canvas.Canvas(path)
    c.drawString(100, 750, f"Archivo: {filename}")
    text_object = c.beginText(100, 730)
    for line in content.split('\n'):
        text_object.textLine(line)
    c.drawText(text_object)
    c.save()
    print(f"PDF creado: {path}")

if __name__ == "__main__":
    create_sample_pdf("Ficha_Bomba_Hidraulica.pdf", "Esta es una ficha técnica de una bomba hidráulica industrial.\nModelo: BH-2000\nPresión máxima: 3000 PSI\nFlujo: 15 GPM.\nFabricado por: Industrias Aventi.")
    create_sample_pdf("Manual_Valvula_Presion.pdf", "Manual de operación de la válvula de presión serie VP-10.\nInstrucciones de seguridad y mantenimiento preventivo.\nInstalar en superficies planas y secas.")
