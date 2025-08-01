# TwistyVoice CSV Setup Guide

TwistyVoice has been updated to use CSV files for customer data management instead of the Square API. This provides more flexibility and control over your customer data.

## CSV File Structure

### customers.csv
The main customer data file should be located at `data/customers.csv` with the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `first_name` | Customer's first name | Alice |
| `last_name` | Customer's last name | Johnson |
| `phone_number` | Phone number with country code | +15551234567 |
| `email` | Email address | alice@example.com |
| `total_visits` | Number of previous visits | 8 |
| `total_spent` | Total amount spent | 480.00 |
| `preferred_services` | Comma-separated services | braids,styling |
| `visit_frequency` | How often they visit | monthly |
| `preferred_stylist` | Preferred stylist name | Tanya |
| `opt_out_calls` | Don't call (true/false) | false |
| `opt_out_sms` | Don't text (true/false) | false |
| `preferred_contact_time` | Best time to contact | afternoon |

### services.csv
Service catalog will be automatically created at `data/services.csv` with these columns:
- `id` - Unique service identifier
- `name` - Service name
- `description` - Service description
- `duration_minutes` - How long the service takes
- `price` - Service price
- `category` - Service category (cut, color, braids, etc.)

### bookings.csv
Booking data will be stored at `data/bookings.csv` with these columns:
- `id` - Unique booking identifier
- `customer_id` - Customer identifier
- `service_name` - Name of the booked service
- `stylist_name` - Assigned stylist
- `appointment_date` - Date in YYYY-MM-DD format
- `appointment_time` - Time in HH:MM format
- `duration_minutes` - Service duration
- `status` - Booking status (confirmed, cancelled, completed)
- `customer_note` - Any customer notes
- `created_at` - When booking was created

## Setup Instructions

1. **Prepare your customer data**: Export your customer data to CSV format and place it at `data/customers.csv`

2. **Run the setup script**:
   ```bash
   python scripts/setup.py
   ```

3. **Verify the setup**: The script will:
   - Create database tables
   - Load customers from your CSV file
   - Create sample services if needed
   - Load sample promotions

## Benefits of CSV Approach

- **No API dependencies**: No need for Square API keys or external service dependencies
- **Full data control**: You own and control all your customer data
- **Easy data management**: Update customer information by editing CSV files
- **Backup friendly**: Simple file-based backup and restore
- **Migration ready**: Easy to import from any existing system

## Data Management

### Adding New Customers
1. Add new rows to `data/customers.csv`
2. Run the setup script again to import new customers

### Updating Customer Information
1. Edit the customer's row in `data/customers.csv`
2. Either run the setup script or manually update the database

### Viewing Bookings
Check `data/bookings.csv` to see all bookings made through the system.

## Migration from Square

If you were previously using Square API:
1. Export your customer data from Square
2. Convert it to the CSV format described above
3. Update any references to `square_customer_id` in your data to use the new format
4. Run the setup script to import your data

The system will automatically handle the transition and maintain all your existing customer relationships and booking history.
