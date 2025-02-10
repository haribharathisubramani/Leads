# Updated Changes for Production Deployment

## 1. Update main.py
In your production Replit, update the delete lead section in `main.py` with:

```python
# Add delete button outside the form
if st.button("🗑️ Delete Lead", key=f"delete_{idx}"):
    if delete_lead(idx):
        st.success("Lead deleted successfully!")
        st.rerun()
    else:
        st.error("Failed to delete lead. Please check if the lead exists and try again.")
```

## 2. Update utils/data_handler.py
In your production Replit, update the delete_lead function in `utils/data_handler.py` with:

```python
def delete_lead(index):
    """Delete a lead and move it to trash"""
    try:
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            if 0 <= index < len(df):
                # Get the lead data before deletion
                lead_data = df.iloc[index].to_dict()

                # Save to deleted_leads first
                if save_deleted_lead(lead_data, st.session_state.username):
                    # Remove from active leads
                    df = df.drop(index=index)
                    df = df.reset_index(drop=True)
                    df.to_csv(DATA_FILE, index=False)
                    return True
                return False
        return False
    except Exception as e:
        print(f"Error deleting lead: {str(e)}")
        return False
```

After updating these files in your production Replit:
1. Click the "Run" button to restart the application
2. Test the lead deletion functionality to ensure it works correctly
