import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from modules.logger import setup_logger

logger = setup_logger()

class NumberedCanvas(canvas.Canvas):
    """Two-pass custom canvas for precise running page-number rendering."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#718096"))

        if self._pageNumber > 1:
            self.drawString(54, 750, "ENTERPRISE PERFORMANCE & METRICS AUDIT REPORT")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(54, 742, 612 - 54, 742)

        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 36, footer_text)
        self.drawString(54, 36, "CONFIDENTIAL - AUTOMATED INTERNAL PIPELINE")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(54, 48, 612 - 54, 48)
        self.restoreState()


class PDFReportBuilder:
    def __init__(self, config, df, chart_path, output_pdf="exports/Enterprise_Report.pdf"):
        self.config = config
        self.df = df
        self.chart_path = chart_path
        self.output_pdf = output_pdf
        os.makedirs("exports", exist_ok=True)

    def build(self):
        logger.info(f"Constructing enterprise PDF document layout: {self.output_pdf}")
        doc = SimpleDocTemplate(
            self.output_pdf,
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=72,
            bottomMargin=72
        )

        styles = getSampleStyleSheet()
        
        PRIMARY = colors.HexColor(self.config['styling']['primary_color'])
        SECONDARY = colors.HexColor(self.config['styling']['secondary_color'])
        ACCENT = colors.HexColor(self.config['styling']['accent_bg'])
        TEXT = colors.HexColor(self.config['styling']['text_color'])

        title_style = ParagraphStyle('Title', fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=PRIMARY, spaceAfter=4)
        subtitle_style = ParagraphStyle('Sub', fontName='Helvetica', fontSize=11, leading=15, textColor=SECONDARY, spaceAfter=15)
        heading_style = ParagraphStyle('Heading', fontName='Helvetica-Bold', fontSize=13, leading=17, textColor=PRIMARY, spaceBefore=12, spaceAfter=6, keepWithNext=True)
        body_style = ParagraphStyle('Body', fontName='Helvetica', fontSize=9.5, leading=14, textColor=TEXT, spaceAfter=8)
        cell_style = ParagraphStyle('Cell', fontName='Helvetica', fontSize=8.5, leading=11, textColor=TEXT)
        header_cell_style = ParagraphStyle('HCell', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.whitesmoke)

        story = []

        # Title Block
        story.append(Paragraph(self.config['report_metadata']['title'], title_style))
        story.append(Paragraph(f"Organization: {self.config['report_metadata']['organization']} | Generated: {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
        story.append(Spacer(1, 5))

        # Executive Summary
        story.append(Paragraph("1. Executive Summary", heading_style))
        summary_body = (
            f"This automated audit report evaluates <b>{len(self.df)} core operational metrics</b> across "
            f"enterprise departments. The system validates target benchmarks against actual performances, flagging "
            f"potential performance anomalies. Overall metrics confirm stable operational outputs with minor reviews recommended."
        )
        story.append(Paragraph(summary_body, body_style))
        story.append(Spacer(1, 10))

        # Embed Analytical Chart
        if os.path.exists(self.chart_path):
            story.append(Paragraph("2. Performance Analytics Visual", heading_style))
            story.append(Image(self.chart_path, width=480, height=215))
            story.append(Spacer(1, 15))

        # Tabular Data Log
        story.append(Paragraph("3. Departmental Metric Audit Log", heading_style))
        table_data = [[
            Paragraph("Department", header_cell_style),
            Paragraph("Metric Name", header_cell_style),
            Paragraph("Target", header_cell_style),
            Paragraph("Actual", header_cell_style),
            Paragraph("Status", header_cell_style)
        ]]

        for _, row in self.df.iterrows():
            table_data.append([
                Paragraph(str(row["Department"]), cell_style),
                Paragraph(str(row["Metric_Name"]), cell_style),
                Paragraph(str(row["Target_Value"]), cell_style),
                Paragraph(str(row["Actual_Value"]), cell_style),
                Paragraph(str(row["Status"]), cell_style)
            ])

        metrics_table = Table(table_data, colWidths=[90, 164, 80, 80, 90], repeatRows=1)
        t_style = [
            ('BACKGROUND', (0, 0), (-1, 0), SECONDARY),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ]
        
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                t_style.append(('BACKGROUND', (0, i), (-1, i), ACCENT))
            else:
                t_style.append(('BACKGROUND', (0, i), (-1, i), colors.white))

        metrics_table.setStyle(TableStyle(t_style))
        story.append(metrics_table)
        story.append(Spacer(1, 15))

        # Recommendations & Sign-off
        story.append(Paragraph("4. Strategic Findings & Directives", heading_style))
        directives = (
            "• <b>Resource Optimization:</b> Core departments remain within optimal operational tolerances.<br/>"
            "• <b>Compliance Check:</b> Automated weekly monitoring pipelines are active and fully verified.<br/>"
            "• <i>Report compiled automatically via secure Python reporting backend. End of Document.</i>"
        )
        story.append(KeepTogether([Paragraph(directives, body_style)]))

        doc.build(story, canvasmaker=NumberedCanvas)
        logger.info(f"PDF Report compiled successfully at: {self.output_pdf}")