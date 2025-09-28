import os
import cv2
import numpy as np
from PIL import Image, ImageStat
import re
from datetime import datetime
from typing import Dict, Any, List
import json

def analyze_image_quality(image_path):
    """
    Simple image quality analysis for tampering detection
    Returns quality metrics that contribute to suspicion score
    """
    try:
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            return {"error": "Could not load image", "quality_score": 0.8}
        
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 1. Blur Detection (Laplacian variance)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        is_blurry = blur_score < 100  # Lower = more blurry
        
        # 2. Brightness Analysis
        brightness = np.mean(gray)
        is_too_dark = brightness < 50
        is_too_bright = brightness > 200
        
        # 3. Contrast Analysis
        contrast = gray.std()
        is_low_contrast = contrast < 30
        
        # Calculate quality score (0 = good, 1 = suspicious)
        quality_issues = 0
        if is_blurry: quality_issues += 0.3
        if is_too_dark or is_too_bright: quality_issues += 0.2
        if is_low_contrast: quality_issues += 0.2
        
        return {
            "blur_score": blur_score,
            "brightness": brightness,
            "contrast": contrast,
            "quality_score": min(quality_issues, 1.0),
            "issues": {
                "blurry": is_blurry,
                "poor_lighting": is_too_dark or is_too_bright,
                "low_contrast": is_low_contrast
            }
        }
        
    except Exception as e:
        print(f"Image quality analysis error: {e}")
        return {"error": str(e), "quality_score": 0.5}

def analyze_text_patterns(ocr_text):
    """
    Simple text pattern analysis for document validation
    """
    try:
        if not ocr_text or len(ocr_text.strip()) < 10:
            return {"error": "Insufficient text", "text_score": 0.8}
        
        # 1. Check for common certificate/document keywords
        cert_keywords = [
            'certificate', 'diploma', 'degree', 'university', 'college',
            'awarded', 'completed', 'graduated', 'issued', 'authorized'
        ]
        
        text_lower = ocr_text.lower()
        keyword_matches = sum(1 for word in cert_keywords if word in text_lower)
        has_cert_keywords = keyword_matches >= 2
        
        # 2. Check for suspicious patterns
        suspicious_patterns = [
            r'\b[A-Z]{10,}\b',  # Too many consecutive capitals
            r'\d{4}-\d{4}-\d{4}',  # Credit card-like numbers
            r'[^\w\s]{5,}',  # Too many special characters
        ]
        
        suspicious_matches = sum(1 for pattern in suspicious_patterns 
                               if re.search(pattern, ocr_text))
        
        # 3. Date validation
        date_pattern = r'\b(19|20)\d{2}\b'
        dates = re.findall(date_pattern, ocr_text)
        has_reasonable_dates = len(dates) > 0
        
        # Calculate text score
        text_issues = 0
        if not has_cert_keywords: text_issues += 0.4
        if suspicious_matches > 0: text_issues += 0.3
        if not has_reasonable_dates: text_issues += 0.2
        
        return {
            "keyword_matches": keyword_matches,
            "suspicious_patterns": suspicious_matches,
            "dates_found": len(dates),
            "text_score": min(text_issues, 1.0),
            "issues": {
                "missing_keywords": not has_cert_keywords,
                "suspicious_text": suspicious_matches > 0,
                "no_dates": not has_reasonable_dates
            }
        }
        
    except Exception as e:
        print(f"Text analysis error: {e}")
        return {"error": str(e), "text_score": 0.5}

def calculate_suspicion_score(image_path, ocr_text):
    """
    Calculate real suspicion score based on image and text analysis
    Returns score between 0.0 (authentic) and 1.0 (highly suspicious)
    """
    try:
        # Get image quality analysis
        quality_analysis = analyze_image_quality(image_path)
        quality_score = quality_analysis.get('quality_score', 0.5)
        
        # Get text pattern analysis
        text_analysis = analyze_text_patterns(ocr_text)
        text_score = text_analysis.get('text_score', 0.5)
        
        # Combine scores with weights
        final_score = (quality_score * 0.4) + (text_score * 0.6)
        
        # Return detailed analysis
        return {
            'suspicion_score': round(final_score, 2),
            'quality_analysis': quality_analysis,
            'text_analysis': text_analysis,
            'verdict': get_verdict(final_score),
            'explanation': get_explanation(quality_analysis, text_analysis)
        }
        
    except Exception as e:
        print(f"Error calculating suspicion score: {e}")
        return {
            'suspicion_score': 0.5,
            'error': str(e),
            'verdict': 'error',
            'explanation': 'Could not analyze document properly'
        }

def get_verdict(score):
    """Convert numeric score to human-readable verdict"""
    if score < 0.3:
        return 'likely_authentic'
    elif score < 0.7:
        return 'requires_review'
    else:
        return 'highly_suspicious'

def get_explanation(quality_analysis, text_analysis):
    """Generate human-readable explanation"""
    issues = []
    
    # Quality issues
    if quality_analysis.get('issues', {}).get('blurry'):
        issues.append('Document appears blurry or low quality')
    if quality_analysis.get('issues', {}).get('poor_lighting'):
        issues.append('Poor lighting or contrast detected')
    
    # Text issues
    if text_analysis.get('issues', {}).get('missing_keywords'):
        issues.append('Missing expected certificate keywords')
    if text_analysis.get('issues', {}).get('suspicious_text'):
        issues.append('Suspicious text patterns detected')
    if text_analysis.get('issues', {}).get('no_dates'):
        issues.append('No valid dates found')
    
    if not issues:
        return 'Document appears to be authentic'
    
    return '; '.join(issues)

def process_document(image_path, ocr_text):
    """
    Simple document processing pipeline using real analysis
    """
    try:
        result = calculate_suspicion_score(image_path, ocr_text)
        return {
            "success": True,
            "image_path": image_path,
            "suspicion_score": result['suspicion_score'],
            "verdict": result['verdict'],
            "explanation": result['explanation'],
            "details": {
                "quality_analysis": result.get('quality_analysis', {}),
                "text_analysis": result.get('text_analysis', {})
            }
        }
    except Exception as e:
        print(f"Document processing error: {e}")
        return {
            "success": False,
            "error": str(e),
            "suspicion_score": 0.5,
            "verdict": "error"
        }
