import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

import PyPDF2
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

    def _extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """
        Extract text content from PDF bytes

        Args:
            pdf_content: Raw PDF file bytes

        Returns:
            Extracted text content as string

        Raises:
            PDFProcessingError: If PDF extraction fails
        """
        try:
            pdf_file = BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            text_content = []
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    text = page.extract_text()
                    if text:
                        text_content.append(f"--- Page {page_num + 1} ---\n{text}")
                except Exception as e:
                    raise PDFProcessingError(
                        f"Error extracting text from page {page_num + 1}: {str(e)}"
                    )

            if not text_content:
                raise PDFProcessingError("No text content could be extracted from PDF")

            log.debug(f"Extracted text from PDF: {text_content}")
            return "\n\n".join(text_content)
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
        try:
            # Extract text from PDF first
            statement_text = self._extract_text_from_pdf(pdf_content)

            # Create an assistant for CSV extraction
            assistant = self.client.beta.assistants.create(
                name="Credit Card Statement Processor",
                instructions="""You are a data extraction assistant that processes credit card statements.

Your task is to:
1. Identify all transaction entries in the statement
2. Extract the following columns for each transaction: Date, Description, Amount, Category (if available)
3. Return ONLY a clean CSV format with headers
4. Use comma as delimiter
5. If amount shows debits/credits separately, use negative numbers for debits
6. Clean up the description field to remove extra spaces and special characters
7. Date should be in YYYY-MM-DD format

Return ONLY the CSV data, no explanations or additional text.""",
                model="gpt-4o",
            )

            # Create a thread with the text content
            thread = self.client.beta.threads.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"Extract all transactions from this credit card statement and return them as CSV.\n\nStatement Content:\n{statement_text}",
                    }
                ]
            )

            # Run the assistant
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=thread.id, assistant_id=assistant.id
            )

            if run.status != "completed":
                raise PDFProcessingError(
                    f"Assistant run failed with status: {run.status}"
                )

            # Get all messages and extract complete response
            messages = self.client.beta.threads.messages.list(thread_id=thread.id)

            # Collect all assistant responses
            assistant_responses = []
            for message in messages.data:
                if message.role == "assistant":
                    for content in message.content:
                        if content.type == "text" and hasattr(content, "text"):
                            assistant_responses.append(content.text.value)

            if not assistant_responses:
                raise PDFProcessingError("No response received from OpenAI")

            # Combine all responses
            full_response = "\n".join(assistant_responses)

            # Clean up resources
            try:
                self.client.beta.assistants.delete(assistant.id)
            except Exception:
                pass  # Ignore cleanup errors

            # Extract CSV content from the response
            csv_output = self._extract_csv_from_response(full_response)

            return csv_output

        except PDFProcessingError:
            raise
        except Exception as e:
            raise PDFProcessingError(f"Error processing PDF with OpenAI: {str(e)}")

    def _extract_csv_from_response(self, response: str) -> str:
        """
        Extract CSV content from OpenAI response, removing markdown and extra text

        Args:
            response: Full response text from OpenAI

        Returns:
            Clean CSV content
        """
        csv_output = response.strip()

        # Remove markdown code blocks if present
        if "```" in csv_output:
            lines = csv_output.split("\n")
            in_code_block = False
            csv_lines = []

            for line in lines:
                if line.startswith("```"):
                    in_code_block = not in_code_block
                    continue
                if in_code_block or (not in_code_block and "," in line):
                    csv_lines.append(line)

            csv_output = "\n".join(csv_lines).strip()

        return csv_output
