import frappe
import json
import xml.etree.ElementTree as ET
import csv
from io import StringIO
import re

class FeedParser:
    """Utility class for parsing different feed formats"""
    
    @staticmethod
    def parse_xml(content, xpath=None):
        """
        Parse XML content
        
        Args:
            content (str): XML content
            xpath (str, optional): XPath to extract items. Defaults to None.
        
        Returns:
            list: List of dictionaries containing parsed data
        """
        try:
            root = ET.fromstring(content)
            items = []
            
            # Try to determine the item path if not provided
            if not xpath:
                # Common XML structures
                common_paths = [
                    './/item',
                    './/product',
                    './/products/*',
                    './/items/*',
                    './/*[contains(local-name(), "product")]',
                    './/*[contains(local-name(), "item")]'
                ]
                
                for path in common_paths:
                    elements = root.findall(path)
                    if elements:
                        xpath = path
                        break
            
            # If we have a path, use it
            if xpath:
                elements = root.findall(xpath)
                for element in elements:
                    item_data = {}
                    for child in element:
                        # Handle attributes
                        for attr_name, attr_value in child.attrib.items():
                            item_data[f"{child.tag}_{attr_name}"] = attr_value
                        
                        # Handle text content
                        if child.text and child.text.strip():
                            item_data[child.tag] = child.text.strip()
                        
                        # Handle nested elements
                        for nested in child:
                            if nested.text and nested.text.strip():
                                item_data[f"{child.tag}_{nested.tag}"] = nested.text.strip()
                    
                    # Also include direct attributes of the item element
                    for attr_name, attr_value in element.attrib.items():
                        item_data[attr_name] = attr_value
                    
                    items.append(item_data)
            else:
                # Fallback: try to extract all elements with their paths
                def extract_elements(element, path=""):
                    result = {}
                    current_path = path + "/" + element.tag if path else element.tag
                    
                    # Add text content if present
                    if element.text and element.text.strip():
                        result[current_path] = element.text.strip()
                    
                    # Add attributes
                    for attr_name, attr_value in element.attrib.items():
                        result[f"{current_path}@{attr_name}"] = attr_value
                    
                    # Process children
                    for child in element:
                        child_data = extract_elements(child, current_path)
                        result.update(child_data)
                    
                    return result
                
                items.append(extract_elements(root))
            
            return items
        except Exception as e:
            frappe.log_error(f"XML parsing error: {str(e)}", "Feed Parse Error")
            raise
    
    @staticmethod
    def parse_csv(content, delimiter=',', quotechar='"'):
        """
        Parse CSV content
        
        Args:
            content (str): CSV content
            delimiter (str, optional): CSV delimiter. Defaults to ','.
            quotechar (str, optional): CSV quote character. Defaults to '"'.
        
        Returns:
            list: List of dictionaries containing parsed data
        """
        try:
            items = []
            # Try to detect the delimiter if not explicitly provided
            if delimiter == ',':
                # Count occurrences of common delimiters
                first_line = content.split('\n')[0] if content else ""
                delimiters = {',': 0, ';': 0, '\t': 0, '|': 0}
                
                for d in delimiters:
                    delimiters[d] = first_line.count(d)
                
                # Use the most frequent delimiter
                max_count = 0
                for d, count in delimiters.items():
                    if count > max_count:
                        max_count = count
                        delimiter = d
            
            csv_reader = csv.DictReader(StringIO(content), delimiter=delimiter, quotechar=quotechar)
            for row in csv_reader:
                # Clean up keys (remove whitespace)
                cleaned_row = {k.strip(): v for k, v in row.items()}
                items.append(cleaned_row)
            
            return items
        except Exception as e:
            frappe.log_error(f"CSV parsing error: {str(e)}", "Feed Parse Error")
            raise
    
    @staticmethod
    def parse_json(content):
        """
        Parse JSON content
        
        Args:
            content (str): JSON content
        
        Returns:
            list: List of dictionaries containing parsed data
        """
        try:
            data = json.loads(content)
            
            # Handle different JSON structures
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Try to find an array in the JSON
                for key, value in data.items():
                    if isinstance(value, list) and value and isinstance(value[0], dict):
                        # Found an array of objects
                        return value
                
                # If no array found, return the dict as a single item
                return [data]
            else:
                # Return as a single item
                return [{"value": data}]
        except Exception as e:
            frappe.log_error(f"JSON parsing error: {str(e)}", "Feed Parse Error")
            raise
    
    @staticmethod
    def detect_format(content):
        """
        Detect the format of the content
        
        Args:
            content (str): Content to detect format for
        
        Returns:
            str: Detected format ("XML", "CSV", "JSON", or "UNKNOWN")
        """
        # Check if it's XML
        if content.strip().startswith('<?xml') or re.match(r'^\s*<[^>]+>', content):
            return "XML"
        
        # Check if it's JSON
        try:
            json.loads(content)
            return "JSON"
        except:
            pass
        
        # Check if it's CSV (simple heuristic)
        lines = content.strip().split('\n')
        if len(lines) > 1:
            header = lines[0]
            if ',' in header or ';' in header or '\t' in header:
                # Check if all lines have approximately the same number of delimiters
                delimiters = [',', ';', '\t']
                for d in delimiters:
                    if d in header:
                        header_count = header.count(d)
                        # Check a few sample lines
                        is_consistent = True
                        for i in range(1, min(5, len(lines))):
                            if abs(lines[i].count(d) - header_count) > 1:
                                is_consistent = False
                                break
                        
                        if is_consistent:
                            return "CSV"
        
        return "UNKNOWN"
    
    @staticmethod
    def parse(content, format_type=None):
        """
        Parse content based on format
        
        Args:
            content (str): Content to parse
            format_type (str, optional): Format type ("XML", "CSV", "JSON"). 
                                        If None, format will be auto-detected.
        
        Returns:
            list: List of dictionaries containing parsed data
        """
        if not format_type:
            format_type = FeedParser.detect_format(content)
        
        if format_type == "XML":
            return FeedParser.parse_xml(content)
        elif format_type == "CSV":
            return FeedParser.parse_csv(content)
        elif format_type == "JSON":
            return FeedParser.parse_json(content)
        else:
            frappe.log_error(f"Unsupported format: {format_type}", "Feed Parse Error")
            raise ValueError(f"Unsupported format: {format_type}")