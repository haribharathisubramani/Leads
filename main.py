import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from utils.data_handler import save_lead, load_leads, filter_leads, update_lead, delete_lead, generate_daily_report, generate_monthly_report, get_deleted_leads, get_pending_followups
from utils.pdf_generator import generate_pdf
from utils.auth import require_login, show_login_page, show_admin_console

# Update the page configuration
st.set_page_config(
    page_title="Hari's Project",
    page_icon="📊",
    layout="wide"
)

# Initialize session state for navigation
if 'page' not in st.session_state:
    st.session_state.page = "Add Lead"

# Hide Streamlit menu and footer
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Custom footer
st.markdown(
    """
    <div style='position: fixed; bottom: 0; width: 100%; text-align: center; padding: 10px; background-color: white;'>
        Made with ❤️ by Hari for my team mates
    </div>
    """,
    unsafe_allow_html=True
)

# Custom CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def show_leads_view():
    st.header("View Leads")

    # Filter options
    col1, col2, col3 = st.columns(3)

    # List of month names
    months = [
        "All", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    with col1:
        month = st.selectbox(
            "Select Month",
            months
        )

    with col2:
        status_filter = st.multiselect(
            "Lead Status",
            ["Student", "Working", "Unemployed", "Fresher"]
        )

    with col3:
        call_status_filter = st.multiselect(
            "Call Status",
            ["Call taken", "Busy", "RNP", "Out of service", "Abroad", "Cut the call"]
        )

    # Add creator filter for admin users
    if st.session_state.is_admin:
        creator_filter = st.multiselect(
            "Filter by Creator",
            ["All"] + list(load_leads(is_admin=True)['created_by'].unique())
        )

    # Load and filter leads based on user access
    leads = load_leads(
        username=st.session_state.username,
        is_admin=st.session_state.is_admin
    )

    # Apply creator filter for admin users
    if st.session_state.is_admin and creator_filter and "All" not in creator_filter:
        leads = leads[leads['created_by'].isin(creator_filter)]

    # Sort leads by creation date (most recent first)
    leads['created_at'] = pd.to_datetime(leads['created_at'])
    leads = leads.sort_values('created_at', ascending=False)

    # Convert month name to number for filtering
    if month != "All":
        month_num = months.index(month)
    else:
        month_num = "All"

    filtered_leads = filter_leads(leads, month_num, status_filter, call_status_filter)

    # Add tab for viewing active/deleted leads
    tab1, tab2 = st.tabs(["Active Leads", "Trash"])

    with tab1:
        if not filtered_leads.empty:
            # Display leads with edit buttons
            for idx, lead in filtered_leads.iterrows():
                with st.expander(
                    f"📞 {lead['name']} - {lead['phone']}" +
                    (f" [{str(lead.get('created_by', ''))}]" if st.session_state.is_admin else '')
                ):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        if st.session_state.is_admin:
                            st.markdown(f"**👤 Created by:** {str(lead.get('created_by', 'Unknown'))}")
                            created_at = pd.to_datetime(lead['created_at'])
                            if pd.notna(created_at):
                                st.markdown(f"**🕒 Created at:** {created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                            st.markdown("---")

                        st.write(f"**Email:** {lead.get('email', '')}")
                        st.write(f"**Lead Status:** {lead['lead_status']}")
                        st.write(f"**Call Status:** {lead['call_status']}")
                        st.write(f"**Temperature:** {lead.get('lead_temperature', 'Not specified')}")

                        # Display initial remarks
                        if lead.get('notes'):
                            st.markdown("**📝 Initial Remarks:**")
                            st.info(str(lead['notes']))

                        # Display followup history
                        followup_notes = lead.get('followup_notes', '')
                        if followup_notes and not pd.isna(followup_notes):  # Check if notes exist and are not NaN
                            st.markdown("**📋 Followup History:**")
                            notes_list = str(followup_notes).strip().split('\n')
                            for note in reversed(notes_list):  # Show most recent first
                                if note.strip():  # Only show non-empty notes
                                    st.warning(note)

                    with col2:
                        # Edit form with proper error handling
                        with st.form(key=f"edit_form_{idx}"):
                            # Handle lead status with default value
                            current_status = lead.get('lead_status', 'Student')
                            if pd.isna(current_status):
                                current_status = 'Student'

                            new_status = st.selectbox(
                                "Update Lead Status",
                                ["Student", "Working", "Unemployed", "Fresher"],
                                index=["Student", "Working", "Unemployed", "Fresher"].index(current_status)
                            )

                            # Handle call status with default value
                            current_call_status = lead.get('call_status', 'Call taken')
                            if pd.isna(current_call_status):
                                current_call_status = 'Call taken'

                            new_call_status = st.selectbox(
                                "Update Call Status",
                                ["Call taken", "Busy", "RNP", "Out of service", "Abroad", "Cut the call"],
                                index=["Call taken", "Busy", "RNP", "Out of service", "Abroad", "Cut the call"].index(current_call_status)
                            )

                            # Handle lead temperature with default value
                            current_temp = lead.get('lead_temperature', 'Cold')
                            if pd.isna(current_temp):
                                current_temp = 'Cold'

                            new_temperature = st.selectbox(
                                "Update Lead Temperature",
                                ["Hot", "Cold"],
                                index=["Hot", "Cold"].index(current_temp)
                            )

                            # Add followup tracking
                            next_followup = st.date_input(
                                "Schedule Next Followup",
                                min_value=datetime.now().date(),
                                value=None if pd.isna(lead.get('next_followup')) else pd.to_datetime(lead['next_followup']).date()
                            )

                            followup_status = st.selectbox(
                                "Followup Status",
                                ["Pending", "Completed", "Rescheduled", "No Response"],
                                index=["Pending", "Completed", "Rescheduled", "No Response"].index(
                                    lead.get('followup_status', 'Pending') if pd.notna(lead.get('followup_status')) else 'Pending'
                                )
                            )

                            followup_note = st.text_area(
                                "Add Followup Note",
                                key=f"followup_note_{idx}",
                                height=100,
                                disabled=False
                            )

                            if st.form_submit_button("Update Lead"):
                                try:
                                    updated_data = {
                                        "lead_status": new_status,
                                        "call_status": new_call_status,
                                        "lead_temperature": new_temperature,
                                        "last_followup": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        "next_followup": next_followup.strftime("%Y-%m-%d") if next_followup else None,
                                        "followup_status": followup_status
                                    }

                                    # Handle followup notes
                                    if followup_note:
                                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        new_note = f"[{timestamp}] {followup_note}"
                                        current_notes = str(lead.get('followup_notes', ''))
                                        if pd.isna(current_notes):
                                            current_notes = ''
                                        updated_data["followup_notes"] = f"{current_notes}\n{new_note}" if current_notes else new_note

                                    if update_lead(idx, updated_data):
                                        st.success("Lead updated successfully!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to update lead. Please try again.")
                                except Exception as e:
                                    st.error(f"An error occurred: {str(e)}")

                        # Add delete button outside the form
                        if st.button("🗑️ Delete Lead", key=f"delete_{idx}"):
                            if delete_lead(idx):
                                st.success("Lead deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to delete lead. Please check if the lead exists and try again.")

            # Export options
            if st.button("Export to CSV"):
                csv = filtered_leads.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    "leads.csv",
                    "text/csv"
                )
        else:
            st.info("No leads found matching the criteria")

    with tab2:
        if st.session_state.is_admin or st.session_state.is_superuser:
            deleted_leads = get_deleted_leads(is_admin=True)
        else:
            deleted_leads = get_deleted_leads(username=st.session_state.username)

        if not deleted_leads.empty:
            for idx, lead in deleted_leads.iterrows():
                with st.expander(f"🗑️ {lead['name']} - {lead['phone']} (Deleted on: {lead['deleted_at']})"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**Created by:** {lead.get('created_by', 'Unknown')}")
                        st.write(f"**Deleted by:** {lead.get('deleted_by', 'Unknown')}")
                        st.write(f"**Email:** {lead.get('email', '')}")
                        st.write(f"**Lead Status:** {lead['lead_status']}")
                        st.write(f"**Call Status:** {lead['call_status']}")
                        if lead.get('notes'):
                            st.info(f"**Notes:** {lead['notes']}")
        else:
            st.info("No deleted leads found")


def show_add_lead_form():
    st.header("Add New Lead")

    with st.form("lead_form"):
        col1, col2 = st.columns(2)

        with col1:
            lead_name = st.text_input("Lead Name*")
            phone = st.text_input("Phone Number*")
            email = st.text_input("Email")
            lead_temperature = st.selectbox(
                "Lead Temperature*",
                ["Hot", "Cold"]
            )

        with col2:
            lead_status = st.selectbox(
                "Lead Status*",
                ["Student", "Working", "Unemployed", "Fresher"]
            )
            call_status = st.selectbox(
                "Call Status*",
                ["Call taken", "Busy", "RNP", "Out of service", "Abroad", "Cut the call"]
            )
            details_shared = st.checkbox("Details Shared with Lead", value=False)

        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Save Lead")

        if submitted:
            if not lead_name or not phone:
                st.error("Please fill in all required fields marked with *")
            else:
                lead_data = {
                    "name": lead_name,
                    "phone": phone,
                    "email": email,
                    "lead_status": lead_status,
                    "call_status": call_status,
                    "notes": notes,
                    "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "last_followup": "",
                    "followup_notes": "",
                    "lead_temperature": lead_temperature,
                    "details_shared": details_shared,
                    "created_by": st.session_state.username,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                save_lead(lead_data, st.session_state.username)
                st.success("Lead saved successfully!")

def show_daily_summary():
    st.header("Performance Summary")

    # Initialize selected_creator before the if statement
    selected_creator = "All"

    # Add creator selection for admin users
    if st.session_state.is_admin:
        creators = ["All"] + list(load_leads(is_admin=True)['created_by'].unique())
        selected_creator = st.selectbox("Select Team Member", creators)

    # Add time period selection
    col1, col2 = st.columns(2)
    with col1:
        view_type = st.radio("View Type", ["Daily", "Monthly"])

    with col2:
        if view_type == "Monthly":
            months = [
                "All", "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            selected_month = st.selectbox("Select Month", months)
            month_num = months.index(selected_month) if selected_month != "All" else None
        else:
            month_num = None

    try:
        if view_type == "Daily":
            report = generate_daily_report(
                username=st.session_state.username,
                is_admin=st.session_state.is_admin,
                selected_creator=selected_creator if selected_creator != "All" else None
            )
        else:
            report = generate_monthly_report(
                username=st.session_state.username,
                is_admin=st.session_state.is_admin,
                selected_creator=selected_creator if selected_creator != "All" else None,
                month=month_num
            )

        # Display metrics in columns
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Total Leads", report.get("total_leads", 0))
        with col2:
            st.metric("Calls Taken", report.get("calls_taken", 0))
        with col3:
            st.metric("Hot Leads", report.get("hot_leads", 0))
        with col4:
            st.metric("Cold Leads", report.get("cold_leads", 0))
        with col5:
            st.metric("Details Shared", report.get("details_shared", 0))

        # Display breakdowns
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Status Breakdown")
            status_breakdown = report.get("status_breakdown", {})
            if status_breakdown:
                st.json(status_breakdown)
            else:
                st.info("No status data available")

        with col2:
            st.subheader("Call Status Breakdown")
            call_status_breakdown = report.get("call_status_breakdown", {})
            if call_status_breakdown:
                st.json(call_status_breakdown)
            else:
                st.info("No call status data available")

        # Display daily leads chart for monthly view
        if view_type == "Monthly" and "daily_leads" in report and report["daily_leads"]:
            st.subheader("Daily Lead Distribution")
            daily_leads_df = pd.DataFrame.from_dict(
                report["daily_leads"],
                orient='index',
                columns=['count']
            )
            daily_leads_df.index = pd.to_datetime(daily_leads_df.index)
            st.line_chart(daily_leads_df)

    except Exception as e:
        st.error(f"An error occurred while generating the report: {str(e)}")
        st.info("Please try again or contact support if the issue persists.")

def show_reports():
    st.header("Generate Reports")

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input("Start Date")

    with col2:
        end_date = st.date_input("End Date")

    if st.button("Generate PDF Report"):
        leads = load_leads(
            username=st.session_state.username,
            is_admin=st.session_state.is_admin
        )
        filtered_leads = leads[
            (pd.to_datetime(leads['date_added']).dt.date >= start_date) &
            (pd.to_datetime(leads['date_added']).dt.date <= end_date)
        ]

        if not filtered_leads.empty:
            pdf_file = generate_pdf(filtered_leads, start_date, end_date)
            with open(pdf_file, "rb") as f:
                st.download_button(
                    "Download Report",
                    f,
                    "lead_report.pdf",
                    "application/pdf"
                )
        else:
            st.warning("No data available for the selected date range")

@require_login
def main():
    # Sidebar configuration
    with st.sidebar:
        st.title("🎯 Navigation")
        st.markdown("---")

        nav_options = {
            "📝 Add Lead": "Add Lead",
            "👥 View Leads": "View Leads",
            "📊 Reports": "Generate Reports",
            "📈 Daily Summary": "Daily Summary"
        }

        # Add Admin Console option for admin users
        if 'is_admin' in st.session_state and st.session_state.is_admin:
            nav_options["⚙️ Admin Console"] = "Admin Console"

        # Navigation buttons
        for label, value in nav_options.items():
            if st.button(label, use_container_width=True):
                st.session_state.page = value

        # Display assistance info
        st.markdown("---")
        st.markdown("### ℹ️ Need Help?")
        st.markdown("For assistance, please contact Hari")

        # Logout button
        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.rerun()

        # Add followup tracking section to sidebar for "View Leads" page
        if st.session_state.page == "View Leads":
            st.markdown("### 📅 Today's Followups")
            pending_followups = get_pending_followups(
                username=st.session_state.username,
                is_admin=st.session_state.is_admin
            )

            if not pending_followups.empty:
                for _, followup in pending_followups.iterrows():
                    with st.expander(f"📞 {followup['name']}"):
                        st.write(f"**Phone:** {followup['phone']}")
                        next_followup = pd.to_datetime(followup['next_followup']).strftime('%Y-%m-%d') if pd.notna(followup['next_followup']) else 'Not scheduled'
                        st.write(f"**Scheduled:** {next_followup}")
                        st.write(f"**Status:** {followup.get('followup_status', 'Pending')}")
                        if st.button("Mark Complete", key=f"complete_{followup.name}"):
                            update_lead(followup.name, {
                                "followup_status": "Completed",
                                "last_followup": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                            st.rerun()
            else:
                st.info("No followups scheduled for today")


    # Main content based on navigation
    if st.session_state.page == "Admin Console":
        show_admin_console()
    elif st.session_state.page == "Add Lead":
        show_add_lead_form()
    elif st.session_state.page == "View Leads":
        show_leads_view()
    elif st.session_state.page == "Daily Summary":
        show_daily_summary()
    else:
        show_reports()

if __name__ == "__main__":
    main()