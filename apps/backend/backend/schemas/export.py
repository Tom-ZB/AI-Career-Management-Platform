"""
Pydantic schemas for export files (PDF and CSV).
"""
from typing import List, Dict
from pydantic import BaseModel


class ExportConfig(BaseModel):
    """Base schema for export configurations."""
    include_header: bool = True
    include_footer: bool = True
    date_range: Optional[str] = None
    file_name: Optional[str] = None
    fields: List[str]


class PDFExportConfig(ExportConfig):
    """Configuration options for PDF exports."""
    orientation: str = "portrait"
    page_size: str = "A4"
    title: str
    subtitle: Optional[str] = None
    watermark: Optional[str] = None
    logo_path: Optional[str] = None


class CSVExportConfig(ExportConfig):
    """Configuration options for CSV exports."""
    delimiter: str = ","
    encoding: str = "utf-8"
    include_headers: bool = True
    quotes: bool = True


class ExportData(BaseModel):
    """Generic export data model."""
    columns: List[str]
    data: List[List[Any]]
    metadata: Dict[str, str]


class PDFExportContent(BaseModel):
    """Content structure for PDF documents."""
    sections: List[Dict[str, Any]]


class CSVExportContent(BaseModel):
    """Content structure for CSV data."""
    headers: List[str]
    rows: List[List[Any]]
