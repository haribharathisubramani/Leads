#!/bin/bash
# Deployment steps for lead.iamhari.in

# 1. Backup production data
echo "Creating backups..."
ssh username@lead.iamhari.in "cd /path/to/your/app && \
    cp users.db users.db.backup && \
    cp leads_data.csv leads_data.csv.backup"

# 2. Transfer updated files
echo "Transferring updated files..."
scp main.py username@lead.iamhari.in:/path/to/your/app/
scp utils/data_handler.py username@lead.iamhari.in:/path/to/your/app/utils/

# 3. Restart Streamlit server
echo "Restarting Streamlit server..."
ssh username@lead.iamhari.in "sudo systemctl restart streamlit-server"

echo "Deployment completed!"
