import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def after_install():
    """Setup custom fields and other configurations after app installation"""
    create_supplier_custom_fields()

def create_supplier_custom_fields():
    """Create custom fields in Supplier DocType"""
    
    # Add a section for Supplier Feeds in Supplier DocType
    create_custom_field('Supplier', {
        'fieldname': 'supplier_feed_section',
        'label': 'Supplier Feed',
        'fieldtype': 'Section Break',
        'insert_after': 'disabled',
        'collapsible': 1
    })
    
    # Add a field to link to Feed Setup
    create_custom_field('Supplier', {
        'fieldname': 'feed_setups',
        'label': 'Feed Setups',
        'fieldtype': 'HTML',
        'insert_after': 'supplier_feed_section',
        'options': '<div class="feed-setup-links"></div>'
    })
    
    frappe.db.commit()