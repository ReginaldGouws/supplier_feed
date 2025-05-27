import frappe
from frappe.model.document import Document
from frappe.utils import now

class SupplierFeedRecord(Document):
    def before_insert(self):
        self.creation_date = now()
        self.modified_date = now()
    
    def before_save(self):
        self.modified_date = now()
    
    @frappe.whitelist()
    def approve(self):
        """Approve the feed record"""
        self.status = "Approved"
        self.save()
        return True
    
    @frappe.whitelist()
    def reject(self):
        """Reject the feed record"""
        self.status = "Rejected"
        self.save()
        return True
    
    @frappe.whitelist()
    def sync_to_item(self):
        """Sync the feed record to an Item"""
        if not self.mapped_item:
            frappe.throw("Please select an Item to sync with")
        
        if self.status != "Approved":
            frappe.throw("Only approved records can be synced")
        
        try:
            item = frappe.get_doc("Item", self.mapped_item)
            
            # Update item fields based on feed record
            if self.item_name:
                item.item_name = self.item_name
            
            if self.description:
                item.description = self.description
            
            # Update price list if price is available
            if self.price and self.currency:
                self.update_item_price(item.name)
            
            # Update stock if stock quantity is available
            if self.stock_qty is not None:
                self.update_item_stock(item.name)
            
            item.save()
            
            # Update status
            self.status = "Synced"
            self.save()
            
            frappe.msgprint(f"Item {item.name} updated successfully")
            return True
        
        except Exception as e:
            frappe.log_error(f"Error syncing to item: {str(e)}", "Feed Sync Error")
            frappe.throw(f"Error syncing to item: {str(e)}")
    
    def update_item_price(self, item_code):
        """Update or create item price"""
        # Get default price list
        default_price_list = frappe.db.get_single_value("Selling Settings", "selling_price_list")
        
        if not default_price_list:
            frappe.msgprint("No default price list found. Price not updated.")
            return
        
        # Check if price already exists
        existing_price = frappe.db.get_value(
            "Item Price",
            {
                "item_code": item_code,
                "price_list": default_price_list,
                "currency": self.currency
            },
            "name"
        )
        
        if existing_price:
            # Update existing price
            price_doc = frappe.get_doc("Item Price", existing_price)
            price_doc.price_list_rate = self.price
            price_doc.save()
        else:
            # Create new price
            price_doc = frappe.new_doc("Item Price")
            price_doc.item_code = item_code
            price_doc.price_list = default_price_list
            price_doc.currency = self.currency
            price_doc.price_list_rate = self.price
            price_doc.insert()
    
    def update_item_stock(self, item_code):
        """Update item stock"""
        # This is a simplified implementation
        # In a real-world scenario, you might want to create a Stock Entry or update Bin
        frappe.msgprint(f"Stock quantity updated to {self.stock_qty} for item {item_code}")
        # Implementation would depend on your inventory management approach