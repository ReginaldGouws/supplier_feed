frappe.ui.form.on('Feed Setup', {
    refresh: function(frm) {
        // Add button to fetch feed manually
        frm.add_custom_button(__('Fetch Feed Now'), function() {
            frappe.call({
                method: "fetch_feed_manually",
                doc: frm.doc,
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint(__("Feed fetched successfully"));
                        frm.refresh();
                    } else {
                        frappe.msgprint(__("Failed to fetch feed. Check error logs for details."));
                    }
                }
            });
        });
        
        // Add button to view feed records
        frm.add_custom_button(__('View Feed Records'), function() {
            frappe.set_route('List', 'Supplier Feed Record', {feed_setup: frm.doc.name});
        });
    }
});