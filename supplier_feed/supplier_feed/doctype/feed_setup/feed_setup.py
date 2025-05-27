import frappe
from frappe.model.document import Document
import json
import requests
from datetime import datetime
import croniter
import time
from frappe.utils import now_datetime, get_datetime
from supplier_feed.supplier_feed.utils.feed_parser import FeedParser

class FeedSetup(Document):
    def validate(self):
        if self.schedule_type == "Cron Expression" and self.cron_expression:
            try:
                croniter.croniter(self.cron_expression, datetime.now())
            except Exception as e:
                frappe.throw(f"Invalid cron expression: {str(e)}")
    
    @frappe.whitelist()
    def fetch_feed_manually(self):
        """Manually fetch the feed data"""
        return self.fetch_feed()
    
    def fetch_feed(self):
        """Fetch feed data from the configured URL"""
        try:
            response = requests.get(self.feed_url, timeout=30)
            response.raise_for_status()
            
            # Update last fetch time
            self.last_fetch = now_datetime()
            self.save()
            
            # Parse the feed using our utility parser
            data = FeedParser.parse(response.text, self.feed_format)
            
            # Process the parsed data
            self.process_feed_data(data)
            
            return True
        except Exception as e:
            error_msg = f"Error fetching feed {self.feed_name}: {str(e)}"
            frappe.log_error(error_msg, "Feed Fetch Error")
            return False
    
    def process_feed_data(self, data):
        """Process the parsed feed data and create Supplier Feed Records"""
        if not data:
            frappe.msgprint("No data found in the feed")
            return
        
        for item in data:
            # Map fields according to the field mappings
            mapped_data = self.map_fields(item)
            
            # Create a new Supplier Feed Record
            feed_record = frappe.new_doc("Supplier Feed Record")
            feed_record.feed_setup = self.name
            feed_record.supplier = self.supplier
            feed_record.raw_data = json.dumps(item, indent=2)
            
            # Set mapped fields
            for field, value in mapped_data.items():
                if hasattr(feed_record, field):
                    setattr(feed_record, field, value)
            
            feed_record.insert(ignore_permissions=True)
        
        frappe.msgprint(f"Processed {len(data)} items from the feed")
    
    def map_fields(self, item):
        """Map fields from feed data to internal fields based on field mappings"""
        mapped_data = {}
        
        for mapping in self.field_mappings:
            source_field = mapping.source_field
            target_field = mapping.target_field
            
            if source_field in item:
                mapped_data[target_field] = item[source_field]
        
        return mapped_data

def check_feeds_to_fetch():
    """Check which feeds need to be fetched based on their schedule"""
    now = datetime.now()
    
    # Get all enabled feeds
    feeds = frappe.get_all(
        "Feed Setup", 
        filters={"enabled": 1},
        fields=["name", "schedule_type", "cron_expression", "interval_minutes", "last_fetch"]
    )
    
    for feed in feeds:
        should_fetch = False
        
        if feed.schedule_type == "Interval" and feed.interval_minutes:
            # Check if interval has passed since last fetch
            if not feed.last_fetch:
                should_fetch = True
            else:
                last_fetch = get_datetime(feed.last_fetch)
                time_diff = (now - last_fetch.replace(tzinfo=None)).total_seconds() / 60
                if time_diff >= feed.interval_minutes:
                    should_fetch = True
        
        elif feed.schedule_type == "Cron Expression" and feed.cron_expression:
            # Check if cron expression matches current time
            try:
                cron = croniter.croniter(feed.cron_expression, now)
                prev_execution = cron.get_prev(datetime)
                
                if not feed.last_fetch:
                    should_fetch = True
                else:
                    last_fetch = get_datetime(feed.last_fetch)
                    # If the previous execution time is after the last fetch, we should fetch
                    if prev_execution > last_fetch.replace(tzinfo=None):
                        should_fetch = True
            except Exception as e:
                frappe.log_error(f"Cron evaluation error for feed {feed.name}: {str(e)}", "Feed Schedule Error")
        
        if should_fetch:
            try:
                feed_doc = frappe.get_doc("Feed Setup", feed.name)
                feed_doc.fetch_feed()
            except Exception as e:
                frappe.log_error(f"Error fetching feed {feed.name}: {str(e)}", "Feed Fetch Error")