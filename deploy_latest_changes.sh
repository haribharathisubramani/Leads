#!/bin/bash
# Script to deploy latest changes to lead.iamhari.in

# Create backups first
echo "Creating backups..."
ssh username@lead.iamhari.in "cd /path/to/app && \
    cp users.db users.db.backup && \
    cp leads_data.csv leads_data.csv.backup && \
    date >> backup_log.txt"

# Transfer updated files
echo "Deploying updated files..."
scp main.py username@lead.iamhari.in:/path/to/app/
scp utils/data_handler.py username@lead.iamhari.in:/path/to/app/utils/

# Restart Streamlit server
echo "Restarting server..."
ssh username@lead.iamhari.in "sudo systemctl restart streamlit-server"

echo "Deployment completed!"
