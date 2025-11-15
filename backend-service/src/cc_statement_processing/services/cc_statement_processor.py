import asyncio
import csv
import io
import os
import re
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pymupdf.layout
import pymupdf4llm
from openai import OpenAI
from src.common.logger import get_logger

log = get_logger(__name__)


class PDFProcessingError(Exception):
    """Custom exception for PDF processing errors"""

    pass


class CreditCardStatementProcessor:
    """Service to process PDF credit card statements using ChatGPT"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(api_key=self.api_key)
        self.executor = ThreadPoolExecutor(max_workers=3)

    def _extract_tables_as_csv(self, markdown_text: str) -> str:
        """
        Extract all markdown tables from text and join them into a single CSV string.

        Args:
            markdown_text: Text content in markdown format (typically from pymupdf4llm.to_markdown)

        Returns:
            CSV string with all table data combined

        Raises:
            PDFProcessingError: If table extraction fails
        """
        try:
            # Split text into lines
            lines = markdown_text.split("\n")

            all_rows = []
            i = 0
            while i < len(lines):
                line = lines[i].strip()

                # Check if this is a markdown table header (contains |)
                if line.startswith("|") and "|" in line:
                    # Extract header row
                    header = line.split("|")[1:-1]  # Remove empty strings from split
                    header = [cell.strip() for cell in header]

                    # Check if next line is a separator line (|---|---|)
                    if i + 1 < len(lines):
                        separator = lines[i + 1].strip()
                        if separator.startswith("|") and all(
                            cell.strip().replace("-", "").replace(":", "") == ""
                            for cell in separator.split("|")[1:-1]
                        ):
                            # This is a valid table header
                            all_rows.append(header)
                            i += 2  # Skip header and separator

                            # Extract all data rows for this table
                            while i < len(lines):
                                line = lines[i].strip()

                                # Check if line is a table row
                                if line.startswith("|") and "|" in line:
                                    row = line.split("|")[1:-1]  # Remove empty strings
                                    row = [cell.strip() for cell in row]

                                    # Only add non-empty rows
                                    if any(cell for cell in row):
                                        all_rows.append(row)
                                    i += 1
                                else:
                                    # End of this table
                                    break
                            continue

                i += 1

            if not all_rows:
                log.warning("No tables found in markdown text")
                return ""

            # Convert all rows to CSV format
            output = io.StringIO()
            writer = csv.writer(output, lineterminator="\n")
            writer.writerows(all_rows)
            csv_string = output.getvalue()

            log.debug(f"Extracted tables as CSV: {len(all_rows)} rows")
            return csv_string

        except Exception as e:
            raise PDFProcessingError(f"Error extracting tables from markdown: {str(e)}")

    def _extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """
        Extract text content from PDF bytes using pymupdf4llm

        Args:
            pdf_content: Raw PDF file bytes

        Returns:
            Extracted text content as string in Markdown format

        Raises:
            PDFProcessingError: If PDF extraction fails
        """
        try:
            # pymupdf4llm requires a file path, so write bytes to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                tmp_file.write(pdf_content)
                tmp_file_path = tmp_file.name

            try:
                # uses pymupdf.layout
                # This provides better text extraction and structure preservation
                doc = pymupdf.open(tmp_file_path)

                markdown_text = pymupdf4llm.to_markdown(doc)

                log.debug(f"Extracted markdown text: {markdown_text} from PDF")

                if not markdown_text or markdown_text.strip() == "":
                    raise PDFProcessingError(
                        "No text content could be extracted from PDF"
                    )

                log.debug(
                    f"Extracted text from PDF (length: {len(markdown_text)} chars)"
                )
                return markdown_text
            finally:
                # Clean up temporary file
                try:
                    os.unlink(tmp_file_path)
                except Exception:
                    pass
        except PDFProcessingError:
            raise
        except Exception as e:
            if "PDF" in str(type(e).__name__):
                raise PDFProcessingError(f"Invalid or corrupted PDF file: {str(e)}")
            raise PDFProcessingError(f"Error extracting text from PDF: {str(e)}")

    async def process_pdf_statement_async(self, pdf_content: bytes) -> str:
        """
        Process a PDF statement by uploading it directly to OpenAI and return CSV output

        Args:
            pdf_content: Raw PDF file bytes

        Returns:
            CSV string with extracted transaction data

        Raises:
            PDFProcessingError: If any step of the processing fails
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, self.process_pdf_statement, pdf_content
        )

    def ai_extract_csv(self, statement_text: str) -> str:
        """
        Use OpenAI to extract CSV data from statement text

        Args:
            statement_text: Extracted text content from PDF

        Returns:
            CSV string with extracted transaction data

        Raises:
            PDFProcessingError: If OpenAI processing fails
        """
        try:
            system_prompt = """You are a data extraction assistant that processes credit card statements.

Your task is to:
1. Identify all transaction entries in the credit card statement
2. Extract the following columns for each transaction: Date, Description, Amount, Category (if available)
3. Return ONLY a clean CSV format with headers
4. Use comma as delimiter
5. If an amount is an expense, represent it as a number
6. If an amount is a refund, represent it as a negative number
7. Clean up the description field to remove extra spaces and special characters
8. Date should be in YYYY-MM-DD format

Return ONLY the CSV data, no explanations or additional text."""

            user_message = f"Extract all transactions from this credit card statement and return them as CSV. Do not miss any.\n\nStatement Content:\n{statement_text}"

            response = self.client.responses.create(
                model="gpt-5-mini-2025-08-07",
                input=f"""{system_prompt}\n\n{user_message}""",
            )

            log.debug(f"""LLM Input: {system_prompt}\n\n{user_message}""")

            log.debug(response.output_text)
            return response.output_text

        except PDFProcessingError:
            raise
        except Exception as e:
            raise PDFProcessingError(f"Error processing PDF with OpenAI: {str(e)}")

    def process_pdf_statement(self, pdf_content: bytes) -> str:
        """
        Process a PDF statement by converting to text first, then sending to OpenAI for CSV extraction

        Args:
            pdf_content: Raw PDF file bytes

        Returns:
            CSV string with extracted transaction data

        Raises:
            PDFProcessingError: If any step of the processing fails
        """

        statement_text = self._extract_text_from_pdf(pdf_content)
        csv_text = self._extract_tables_as_csv(statement_text)
        log.debug(f"Extracted CSV text from tables: {csv_text}")
        return self.ai_extract_csv(csv_text)
