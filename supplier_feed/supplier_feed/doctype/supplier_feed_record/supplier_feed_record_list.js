frappe.listview_settings['Supplier Feed Record'] = {
    add_fields: ["status"],
    get_indicator: function(doc) {
        if (doc.status === "Pending") {
            return [__("Pending"), "orange", "status,=,Pending"];
        } else if (doc.status === "Approved") {
            return [__("Approved"), "green", "status,=,Approved"];
        } else if (doc.status === "Rejected") {
            return [__("Rejected"), "red", "status,=,Rejected"];
        } else if (doc.status === "Synced") {
            return [__("Synced"), "blue", "status,=,Synced"];
        }
    }
};