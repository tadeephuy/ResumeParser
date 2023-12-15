import xml.etree.ElementTree as ET
import zipfile
import re
import io


class WordDocProcessor():
    """
    The `WordDocProcessor` inherit from `DocumentProcessor` to process the Word Document file scenario

    Args:
        file_content (bytes): the pdf file content bytes that needs to be process
    """
    NAMESPACE_MAP = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

    def __init__(self, file_content: bytes):
        """
        Initializes a `DocumentProcessor` object with the given file content.

        Args:
            file_content (bytes): The content of the file.

        """
        self.file_content = file_content

    def qn(self, tag):
        """
        Stands for 'qualified name', a utility function to turn a namespace
        prefixed tag name into a Clark-notation qualified tag name for lxml.
        """
        prefix, tagroot = tag.split(":")
        return "{{{}}}{}".format(self.NAMESPACE_MAP[prefix], tagroot)

    def xml2text(self, xml):
        """
        Convert XML content to textual content, translating specific tags to their Python equivalent.
        """
        tag_translations = {
            self.qn("w:t"): lambda el: el.text or "",
            self.qn("w:tab"): lambda el: "\t",
            self.qn("w:br"): lambda el: "\n",
            self.qn("w:cr"): lambda el: "\n",
            self.qn("w:p"): lambda el: "\n\n",
        }

        root = ET.fromstring(xml)
        return "".join(tag_translations.get(child.tag, lambda el: "")(child) for child in root.iter())

    def process(self, document) -> str:
        """
        Processes a document and extracts the main text from a DOCX file.

        Args:
            document: The DOCX file to be processed.

        Returns:
            str: The extracted main text from the document.

        """
        # unzip the docx in memory
        with zipfile.ZipFile(document) as zip_file:
            file_list = zip_file.namelist()

            # compile regular expressions for faster matching
            header_re = re.compile("word/header[0-9]*.xml")
            footer_re = re.compile("word/footer[0-9]*.xml")

            # using list comprehensions and generator expressions to minimize explicit for-loops
            headers = (self.xml2text(zip_file.read(fname)) for fname in file_list if header_re.match(fname))
            footers = (self.xml2text(zip_file.read(fname)) for fname in file_list if footer_re.match(fname))

            # get main text
            doc_xml_content = zip_file.read("word/document.xml")

            # concatenate texts
            text = "".join([*headers, self.xml2text(doc_xml_content), *footers])

        return text.strip()

    def load_doc(self):
        """
        Loads the document and processes it to create a list of `Document` objects.

        Returns:
            None

        Raises:
            ValueError: Raised when there is an error with the file.

        """
        try:
            return self.process(io.BytesIO(self.file_content))
        except Exception:
            return ValueError("File error. Please try again")