"""
Export Service - PDF and CSV export functionality.
"""
from typing import Optional, List, Dict, Any
from io import BytesIO, StringIO
from datetime import datetime
from sqlalchemy.orm import Session

from backend.models.job_application import JobApplication
from backend.models.job_opportunity import JobOpportunity
from backend.models.cv import CV


class ExportService:
    """Service for exporting data to PDF and CSV formats."""

    def __init__(self, db: Session):
        self.db = db

    async def export_applications_pdf(
        self, user_id: int, status: Optional[str] = None
    ) -> bytes:
        """
        Export applications as PDF.

        Args:
            user_id: The authenticated user's ID
            status: Optional status filter

        Returns:
            PDF content as bytes
        """
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib.colors import HexColor
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            )

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
            styles = getSampleStyleSheet()
            elements = []

            # Title
            title_style = ParagraphStyle(
                'CustomTitle', parent=styles['Heading1'],
                fontSize=18, spaceAfter=20, textColor=HexColor('#1a1a2e')
            )
            elements.append(Paragraph("Job Applications Report", title_style))
            elements.append(Paragraph(
                f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
                styles['Normal']
            ))
            elements.append(Spacer(1, 20))

            # Get applications
            query = self.db.query(JobApplication).filter(JobApplication.user_id == user_id)
            if status:
                query = query.filter(JobApplication.status == status)
            applications = query.order_by(JobApplication.created_at.desc()).all()

            # Build table data
            table_data = [["Company", "Position", "Status", "Date", "Notes"]]
            for app in applications:
                job = (
                    self.db.query(JobOpportunity)
                    .filter(JobOpportunity.id == app.job_opportunity_id)
                    .first()
                )
                table_data.append([
                    job.company if job else "N/A",
                    job.title if job else "N/A",
                    app.status.value if app.status else "N/A",
                    str(app.application_date.date()) if app.application_date else "N/A",
                    (app.notes or "")[:50] + ("..." if app.notes and len(app.notes) > 50 else ""),
                ])

            # Create table
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#16213e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f5f5f5')),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#cccccc')),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ]))
            elements.append(table)

            # Summary
            elements.append(Spacer(1, 20))
            elements.append(Paragraph(
                f"Total Applications: {len(applications)}",
                styles['Normal']
            ))

            doc.build(elements)
            return buffer.getvalue()

        except ImportError:
            # Fallback if reportlab is not installed
            return b"PDF export requires reportlab library"

    async def export_applications_csv(
        self, user_id: int, status: Optional[str] = None
    ) -> str:
        """
        Export applications as CSV.

        Args:
            user_id: The authenticated user's ID
            status: Optional status filter

        Returns:
            CSV content as string
        """
        import csv

        query = self.db.query(JobApplication).filter(JobApplication.user_id == user_id)
        if status:
            query = query.filter(JobApplication.status == status)
        applications = query.order_by(JobApplication.created_at.desc()).all()

        output = StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "ID", "Company", "Position", "Status", "Application Date",
            "Deadline", "Referral Source", "Notes", "Created At"
        ])

        # Data rows
        for app in applications:
            job = (
                self.db.query(JobOpportunity)
                .filter(JobOpportunity.id == app.job_opportunity_id)
                .first()
            )
            writer.writerow([
                app.id,
                job.company if job else "",
                job.title if job else "",
                app.status.value if app.status else "",
                str(app.application_date) if app.application_date else "",
                str(app.deadline) if app.deadline else "",
                app.referral_source or "",
                (app.notes or "").replace("\n", " "),
                str(app.created_at),
            ])

        return output.getvalue()