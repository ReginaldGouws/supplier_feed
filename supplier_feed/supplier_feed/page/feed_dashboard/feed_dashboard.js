frappe.pages['feed-dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Supplier Feed Dashboard',
        single_column: true
    });
    
    // Initialize page
    frappe.feed_dashboard = new FeedDashboard(page);
};

class FeedDashboard {
    constructor(page) {
        this.page = page;
        this.feeds = [];
        this.records = [];
        this.setup_page();
        this.load_data();
    }
    
    setup_page() {
        // Add refresh button
        this.page.set_primary_action('Refresh', () => this.load_data(), 'refresh');
        
        // Add button to create new feed
        this.page.set_secondary_action('New Feed Setup', () => {
            frappe.new_doc('Feed Setup');
        }, 'add');
        
        // Add button to fetch all feeds
        this.page.add_menu_item('Fetch All Enabled Feeds', () => {
            frappe.call({
                method: "supplier_feed.supplier_feed.doctype.feed_setup.feed_setup.check_feeds_to_fetch",
                callback: (r) => {
                    frappe.msgprint(__("Feed fetch process initiated"));
                    setTimeout(() => this.load_data(), 3000);
                }
            });
        });
        
        // Create sections
        this.page.main.html(`
            <div class="feed-dashboard">
                <div class="feed-section">
                    <h5>Feed Setups</h5>
                    <div class="feed-setups-container"></div>
                </div>
                <div class="feed-section">
                    <h5>Recent Feed Records</h5>
                    <div class="feed-records-container"></div>
                </div>
                <div class="feed-section">
                    <h5>Feed Statistics</h5>
                    <div class="feed-stats-container"></div>
                </div>
            </div>
        `);
        
        // Add some basic styling
        this.page.main.find('.feed-dashboard').css({
            'display': 'flex',
            'flex-direction': 'column',
            'gap': '20px'
        });
        
        this.page.main.find('.feed-section').css({
            'background-color': '#f8f8f8',
            'border-radius': '5px',
            'padding': '15px',
            'box-shadow': '0 1px 3px rgba(0,0,0,0.1)'
        });
    }
    
    load_data() {
        this.load_feeds();
        this.load_records();
        this.load_stats();
    }
    
    load_feeds() {
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Feed Setup',
                fields: ['name', 'feed_name', 'supplier', 'feed_format', 'enabled', 'last_fetch', 'feed_url'],
                limit: 50,
                order_by: 'modified desc'
            },
            callback: (r) => {
                this.feeds = r.message || [];
                this.render_feeds();
            }
        });
    }
    
    load_records() {
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Supplier Feed Record',
                fields: ['name', 'feed_setup', 'supplier', 'status', 'item_code', 'item_name', 'creation_date'],
                limit: 20,
                order_by: 'creation_date desc'
            },
            callback: (r) => {
                this.records = r.message || [];
                this.render_records();
            }
        });
    }
    
    load_stats() {
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Supplier Feed Record',
                fields: ['status', 'COUNT(*) as count'],
                group_by: 'status'
            },
            callback: (r) => {
                const stats = r.message || [];
                this.render_stats(stats);
            }
        });
    }
    
    render_feeds() {
        const container = this.page.main.find('.feed-setups-container');
        
        if (this.feeds.length === 0) {
            container.html('<div class="text-muted">No feed setups found</div>');
            return;
        }
        
        let html = `
            <div class="table-responsive">
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>Feed Name</th>
                            <th>Supplier</th>
                            <th>Format</th>
                            <th>Status</th>
                            <th>Last Fetch</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        this.feeds.forEach(feed => {
            const status = feed.enabled ? 
                '<span class="indicator green">Enabled</span>' : 
                '<span class="indicator gray">Disabled</span>';
            
            html += `
                <tr>
                    <td><a href="/app/feed-setup/${feed.name}">${feed.feed_name}</a></td>
                    <td><a href="/app/supplier/${feed.supplier}">${feed.supplier}</a></td>
                    <td>${feed.feed_format}</td>
                    <td>${status}</td>
                    <td>${feed.last_fetch || 'Never'}</td>
                    <td>
                        <button class="btn btn-xs btn-default fetch-feed" data-feed="${feed.name}">
                            Fetch Now
                        </button>
                    </td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        container.html(html);
        
        // Add event handlers
        container.find('.fetch-feed').on('click', (e) => {
            const feedName = $(e.currentTarget).attr('data-feed');
            this.fetch_feed(feedName);
        });
    }
    
    render_records() {
        const container = this.page.main.find('.feed-records-container');
        
        if (this.records.length === 0) {
            container.html('<div class="text-muted">No feed records found</div>');
            return;
        }
        
        let html = `
            <div class="table-responsive">
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>Feed Setup</th>
                            <th>Supplier</th>
                            <th>Item Code</th>
                            <th>Item Name</th>
                            <th>Status</th>
                            <th>Created</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        this.records.forEach(record => {
            let statusIndicator;
            
            switch(record.status) {
                case 'Pending':
                    statusIndicator = '<span class="indicator orange">Pending</span>';
                    break;
                case 'Approved':
                    statusIndicator = '<span class="indicator green">Approved</span>';
                    break;
                case 'Rejected':
                    statusIndicator = '<span class="indicator red">Rejected</span>';
                    break;
                case 'Synced':
                    statusIndicator = '<span class="indicator blue">Synced</span>';
                    break;
                default:
                    statusIndicator = `<span class="indicator">${record.status}</span>`;
            }
            
            html += `
                <tr>
                    <td><a href="/app/feed-setup/${record.feed_setup}">${record.feed_setup}</a></td>
                    <td><a href="/app/supplier/${record.supplier}">${record.supplier}</a></td>
                    <td>${record.item_code || ''}</td>
                    <td>${record.item_name || ''}</td>
                    <td>${statusIndicator}</td>
                    <td>${record.creation_date || ''}</td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
            <div class="text-right">
                <a href="/app/supplier-feed-record" class="btn btn-sm btn-default">View All Records</a>
            </div>
        `;
        
        container.html(html);
    }
    
    render_stats(stats) {
        const container = this.page.main.find('.feed-stats-container');
        
        if (!stats || stats.length === 0) {
            container.html('<div class="text-muted">No statistics available</div>');
            return;
        }
        
        // Prepare data for chart
        const labels = [];
        const data = [];
        const colors = [];
        
        stats.forEach(stat => {
            labels.push(stat.status);
            data.push(stat.count);
            
            // Assign colors based on status
            switch(stat.status) {
                case 'Pending':
                    colors.push('#ffb878'); // Orange
                    break;
                case 'Approved':
                    colors.push('#57bb8a'); // Green
                    break;
                case 'Rejected':
                    colors.push('#ff8989'); // Red
                    break;
                case 'Synced':
                    colors.push('#5e64ff'); // Blue
                    break;
                default:
                    colors.push('#d3d3d3'); // Gray
            }
        });
        
        // Create HTML for stats
        let html = `
            <div class="row">
                <div class="col-md-6">
                    <div class="chart-container" style="height: 200px;"></div>
                </div>
                <div class="col-md-6">
                    <div class="stats-summary">
                        <h6>Feed Records Summary</h6>
                        <table class="table table-bordered">
                            <thead>
                                <tr>
                                    <th>Status</th>
                                    <th>Count</th>
                                </tr>
                            </thead>
                            <tbody>
        `;
        
        stats.forEach(stat => {
            html += `
                <tr>
                    <td>${stat.status}</td>
                    <td>${stat.count}</td>
                </tr>
            `;
        });
        
        html += `
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        
        container.html(html);
        
        // Create chart
        const chartContainer = container.find('.chart-container')[0];
        new frappe.Chart(chartContainer, {
            data: {
                labels: labels,
                datasets: [
                    {
                        name: "Records",
                        values: data,
                        chartType: 'pie'
                    }
                ]
            },
            colors: colors,
            type: 'pie',
            height: 200
        });
    }
    
    fetch_feed(feedName) {
        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Feed Setup",
                name: feedName
            },
            callback: (r) => {
                if (r.message) {
                    frappe.call({
                        method: "fetch_feed_manually",
                        doc: r.message,
                        callback: (r) => {
                            if (r.message) {
                                frappe.show_alert({
                                    message: __("Feed fetched successfully"),
                                    indicator: 'green'
                                });
                                setTimeout(() => this.load_data(), 2000);
                            } else {
                                frappe.show_alert({
                                    message: __("Failed to fetch feed. Check error logs for details."),
                                    indicator: 'red'
                                });
                            }
                        }
                    });
                }
            }
        });
    }
}