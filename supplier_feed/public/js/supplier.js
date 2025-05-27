frappe.ui.form.on('Supplier', {
    refresh: function(frm) {
        // Add custom button to create new feed setup
        frm.add_custom_button(__('Create Feed Setup'), function() {
            frappe.new_doc('Feed Setup', {
                supplier: frm.doc.name
            });
        }, __('Supplier Feed'));
        
        // Add custom button to view feed setups
        frm.add_custom_button(__('View Feed Setups'), function() {
            frappe.set_route('List', 'Feed Setup', {supplier: frm.doc.name});
        }, __('Supplier Feed'));
        
        // Add custom button to view feed records
        frm.add_custom_button(__('View Feed Records'), function() {
            frappe.set_route('List', 'Supplier Feed Record', {supplier: frm.doc.name});
        }, __('Supplier Feed'));
    }
});