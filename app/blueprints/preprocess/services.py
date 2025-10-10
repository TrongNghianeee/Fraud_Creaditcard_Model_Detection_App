"""
OCR services - Business logic for text extraction from images
"""
import io
import time
from PIL import Image
import pytesseract


class OCRService:
    """Service class for OCR operations using Tesseract"""
    
    # Tesseract path configuration (update this based on your system)
    # For Windows: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    # For Linux/Mac: usually in PATH, no need to set
    
    @staticmethod
    def _configure_tesseract():
        """Configure Tesseract path if needed"""
        import platform
        import os
        
        if platform.system() == 'Windows':
            # Try common installation paths
            possible_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                r'C:\Tesseract-OCR\tesseract.exe',
            ]
            
            # Check if tesseract is in PATH first
            import shutil
            tesseract_in_path = shutil.which('tesseract')
            
            if tesseract_in_path:
                pytesseract.pytesseract.tesseract_cmd = tesseract_in_path
            else:
                # Try common paths
                for path in possible_paths:
                    if os.path.exists(path):
                        pytesseract.pytesseract.tesseract_cmd = path
                        break
    
    @classmethod
    def extract_text_from_image(cls, image_data, language='vie+eng'):
        """
        Extract text from image using Tesseract OCR
        
        Args:
            image_data (bytes): Image binary data
            language (str): Language code for OCR (default: 'vie+eng' for Vietnamese and English)
                           Options: 'eng', 'vie', 'vie+eng', 'chi_sim', 'jpn', etc.
            
        Returns:
            dict: Extraction result with text and metadata
        """
        start_time = time.time()
        
        try:
            # Configure Tesseract
            cls._configure_tesseract()
            
            # Load image from bytes
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Perform OCR with confidence data
            ocr_data = pytesseract.image_to_data(
                image, 
                lang=language,
                output_type=pytesseract.Output.DICT
            )
            
            # Extract text
            text = pytesseract.image_to_string(image, lang=language)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in ocr_data['conf'] if conf != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Processing time
            processing_time = time.time() - start_time
            
            # Clean text
            text = text.strip()
            
            return {
                'success': True,
                'text': text,
                'confidence': round(avg_confidence, 2),
                'language': language,
                'processing_time': round(processing_time, 2),
                'word_count': len(text.split()),
                'char_count': len(text),
                'image_size': {
                    'width': image.width,
                    'height': image.height
                }
            }
            
        except FileNotFoundError as e:
            raise ValueError(
                "Tesseract OCR not found. Please install Tesseract:\n"
                "Windows: https://github.com/UB-Mannheim/tesseract/wiki\n"
                "Linux: sudo apt-get install tesseract-ocr tesseract-ocr-vie\n"
                "Mac: brew install tesseract tesseract-lang"
            )
        except Exception as e:
            raise ValueError(f"OCR extraction failed: {str(e)}")
    
    @classmethod
    def extract_structured_data(cls, image_data, language='vie+eng'):
        """
        Extract structured data from image (words, bounding boxes, confidence)
        
        Args:
            image_data (bytes): Image binary data
            language (str): Language code for OCR
            
        Returns:
            dict: Structured OCR data with word-level information
        """
        start_time = time.time()
        
        try:
            cls._configure_tesseract()
            
            image = Image.open(io.BytesIO(image_data))
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Get detailed OCR data
            ocr_data = pytesseract.image_to_data(
                image,
                lang=language,
                output_type=pytesseract.Output.DICT
            )
            
            # Parse structured data
            words = []
            for i in range(len(ocr_data['text'])):
                if int(ocr_data['conf'][i]) > 0:  # Only include confident detections
                    words.append({
                        'text': ocr_data['text'][i],
                        'confidence': int(ocr_data['conf'][i]),
                        'bounding_box': {
                            'x': ocr_data['left'][i],
                            'y': ocr_data['top'][i],
                            'width': ocr_data['width'][i],
                            'height': ocr_data['height'][i]
                        },
                        'block_num': ocr_data['block_num'][i],
                        'line_num': ocr_data['line_num'][i],
                        'word_num': ocr_data['word_num'][i]
                    })
            
            processing_time = time.time() - start_time
            
            # Full text
            full_text = ' '.join([w['text'] for w in words])
            
            return {
                'success': True,
                'full_text': full_text,
                'words': words,
                'total_words': len(words),
                'language': language,
                'processing_time': round(processing_time, 2)
            }
            
        except Exception as e:
            raise ValueError(f"Structured OCR extraction failed: {str(e)}")
