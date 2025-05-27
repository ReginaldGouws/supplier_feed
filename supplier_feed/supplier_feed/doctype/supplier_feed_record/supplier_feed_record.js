frappe.ui.form.on('Supplier Feed Record', {
    refresh: function(frm) {
        // Add buttons based on status
        if (frm.doc.status === "Pending") {
            frm.add_custom_button(__('Approve'), function() {
                frappe.call({
                    method: "approve",
                    doc: frm.doc,
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint(__("Record approved"));
                            frm.refresh();
                        }
                    }
                });
            }).addClass('btn-primary');
            
            frm.add_custom_button(__('Reject'), function() {
                frappe.call({
                    method: "reject",
                    doc: frm.doc,
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint(__("Record rejected"));
                            frm.refresh();
                        }
                    }
                });
            });
        }
        
        if (frm.doc.status === "Approved") {
            frm.add_custom_button(__('Sync to Item'), function() {
                if (!frm.doc.mapped_item) {
                    frappe.msgprint(__("Please select an Item to sync with"));
                    return;
                }
                
                frappe.call({
                    method: "sync_to_item",
                    doc: frm.doc,
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint(__("Record synced to item"));
                            frm.refresh();
                        }
                    }
                });
            }).addClass('btn-primary');
        }
        
        // Add button to view mapped item
        if (frm.doc.mapped_item) {
            frm.add_custom_button(__('View Item'), function() {
                frappe.set_route('Form', 'Item', frm.doc.mapped_item);
            });
        }
        
        // Add button to find and link item
        frm.add_custom_button(__('Find Item by SKU'), function() {
            if (!frm.doc.item_code) {
                frappe.msgprint(__("No Item Code/SKU available"));
                return;
            }
            
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Item",
                    filters: {
                        item_code: frm.doc.item_code
                    },
                    fields: ["name", "item_name"]
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        frm.set_value("mapped_item", r.message[0].name);
                        frm.save();
                        frappe.msgprint(__("Item found and linked"));
                    } else {
                        frappe.msgprint(__("No matching item found"));
                    }
                }
            });
        });
    }
});