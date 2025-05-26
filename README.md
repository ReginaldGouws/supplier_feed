# Supplier Feed

A custom ERPNext module for managing and importing supplier feeds in XML, CSV, and JSON format.

## Features

- **Feed Setup DocType**: Configure supplier feed sources with URL, format, and schedule
- **Supplier Feed Record DocType**: Temporarily store parsed product data for validation
- **Integration with Supplier DocType**: Access feed configurations from Supplier form
- **Scheduled Fetching**: Automatically fetch feeds based on schedule
- **Manual Trigger**: Fetch feeds manually before enabling schedule
- **Review and Sync**: Review and approve data before syncing to ERPNext Items
- **Multi-format Support**: Handle XML, CSV, and JSON formats with flexible parsing

## Installation

### Prerequisites

- ERPNext v15 or later
- Frappe Framework v15 or later

### Steps

1. Change to your bench directory:
   ```
   cd /path/to/your/bench
   ```

2. Get the app from GitHub:
   ```
   bench get-app https://github.com/your-username/supplier_feed
   ```

3. Install the app on your site:
   ```
   bench --site your-site.local install-app supplier_feed
   ```

4. Migrate your database:
   ```
   bench --site your-site.local migrate
   ```

## Usage

### Setting Up a Supplier Feed

1. Go to **Supplier Feed > Feed Setup** and click "New"
2. Enter the feed details:
   - Feed Name: A unique name for this feed
   - Supplier: Select the supplier
   - Feed URL: The URL where the feed can be accessed
   - Feed Format: Select XML, CSV, or JSON
   - Schedule: Configure when to fetch the feed (interval or cron expression)
   - Field Mappings: Map supplier feed fields to internal fields

3. Save the feed setup

### Fetching Feed Data

- **Manual Fetch**: Open the Feed Setup and click "Fetch Feed Now"
- **Scheduled Fetch**: Enable the feed and it will be fetched according to the schedule

### Processing Feed Records

1. Go to **Supplier Feed > Supplier Feed Record** to see fetched records
2. Review each record and click "Approve" or "Reject"
3. For approved records, select a mapped item and click "Sync to Item"

### Accessing from Supplier

1. Open a Supplier record
2. In the "Supplier Feed" section, you'll find links to:
   - Create Feed Setup
   - View Feed Setups
   - View Feed Records

## License

MIT