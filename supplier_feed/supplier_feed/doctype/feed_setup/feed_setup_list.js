frappe.listview_settings['Feed Setup'] = {
    add_fields: ["enabled", "last_fetch"],
    get_indicator: function(doc) {
        if (doc.enabled) {
            return [__("Enabled"), "green", "enabled,=,1"];
        } else {
            return [__("Disabled"), "gray", "enabled,=,0"];
        }
    },
    onload: function(listview) {
        listview.page.add_inner_button(__("Fetch All Enabled Feeds"), function() {
            frappe.call({
                method: "supplier_feed.supplier_feed.doctype.feed_setup.feed_setup.check_feeds_to_fetch",
                callback: function(r) {
                    frappe.msgprint(__("Feed fetch process initiated"));
                    listview.refresh();
                }
            });
        });
    }
};