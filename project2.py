import mysql.connector
from mysql.connector import Error
import streamlit as st
import pandas as pd

# Function to create a database and tables
def create_database_and_tables():
    connection = None
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='yukivid'
        )
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS college_event_management")
        cursor.execute("USE college_event_management")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Events (
            id INT AUTO_INCREMENT PRIMARY KEY,
            event_name VARCHAR(255) NOT NULL,
            event_date DATE NOT NULL,
            event_time TIME NOT NULL,
            venue VARCHAR(255),
            description TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Registrations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id VARCHAR(50) NOT NULL,
            event_id INT NOT NULL,
            FOREIGN KEY (event_id) REFERENCES Events(id)
        )
        """)

        connection.commit()
    except Error as e:
        st.error(f"Database Error: {e}")
    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()

# Function to add an event
def add_event(event_name, event_date, event_time, venue, description):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='yukivid',
            database='college_event_management'
        )
        cursor = connection.cursor()
        sql_insert_query = """
        INSERT INTO Events (event_name, event_date, event_time, venue, description) 
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql_insert_query, (event_name, event_date, event_time, venue, description))
        connection.commit()
        st.success("Event added successfully.")
    except Error as e:
        st.error(f"Error: {e}")
    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()

# Function to view all events
def view_events():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='yukivid',
            database='college_event_management'
        )
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Events")
        records = cursor.fetchall()

        if records:
            df = pd.DataFrame(records, columns=['ID', 'Event Name', 'Event Date', 'Event Time', 'Venue', 'Description'])
            return df
        else:
            return pd.DataFrame(columns=['ID', 'Event Name', 'Event Date', 'Event Time', 'Venue', 'Description'])
    except Error as e:
        st.error(f"Error: {e}")
    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()

# Function to register a student for an event
def register_student(student_id, event_id):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='yukivid',
            database='college_event_management'
        )
        cursor = connection.cursor()

        cursor.execute("SELECT event_date, event_time FROM Events WHERE id = %s", (event_id,))
        event = cursor.fetchone()

        if event is None:
            st.error("Event not found!")
            return

        event_date, event_time = event

        cursor.execute("""
        SELECT COUNT(*) FROM Registrations r
        JOIN Events e ON r.event_id = e.id
        WHERE r.student_id = %s AND e.event_date = %s AND e.event_time = %s
        """, (student_id, event_date, event_time))

        conflict_count = cursor.fetchone()[0]

        if conflict_count > 0:
            st.warning("You are already registered for an event at this time!")
            return

        sql_insert_query = "INSERT INTO Registrations (student_id, event_id) VALUES (%s, %s)"
        cursor.execute(sql_insert_query, (student_id, event_id))
        connection.commit()
        st.success("Registration successful.")
    except Error as e:
        st.error(f"Error: {e}")
    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()

# Function to view registrations for a specific event
def view_registrations(event_id):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='yukivid',
            database='college_event_management'
        )
        cursor = connection.cursor()

        cursor.execute("""
        SELECT r.student_id FROM Registrations r
        WHERE r.event_id = %s
        """, (event_id,))
        records = cursor.fetchall()

        return [row[0] for row in records]
    except Error as e:
        st.error(f"Error: {e}")
    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()

# Function to cancel student registration
def cancel_registration(student_id, event_id):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='yukivid',
            database='college_event_management'
        )
        cursor = connection.cursor()
        sql_delete_query = "DELETE FROM Registrations WHERE student_id = %s AND event_id = %s"
        cursor.execute(sql_delete_query, (student_id, event_id))
        connection.commit()
        if cursor.rowcount > 0:
            st.success("Registration canceled successfully.")
        else:
            st.warning("No registration found with the provided details.")
    except Error as e:
        st.error(f"Error: {e}")
    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()

# Custom CSS for styling
def add_custom_css():
    st.markdown("""
        <style>
        .main-title { font-size: 2.5em; color: #4B4B4B; text-align: center; margin-bottom: 20px; font-weight: bold; }
        .sidebar .sidebar-content { background-color: #f4f4f4; padding: 20px; border-radius: 5px; }
        .stButton>button { 
            background-color: #4CAF50; color: white; border: None; 
            border-radius: 5px; padding: 10px 20px; font-size: 16px; 
            transition: background-color 0.3s ease; 
        }
        .stButton>button:hover { background-color: #45a049; }

        .event-card { 
            background-color: #FFFFFF; border-radius: 8px; padding: 20px; 
            margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); 
        }
        .event-title { font-size: 1.5em; font-weight: bold; color: #333; margin-bottom: 10px; }
        .event-info { font-size: 1em; color: #555; }
        
        .stDataFrame { border-radius: 5px; border: 1px solid #ddd; padding: 5px; }

        @media (max-width: 768px) {
            .main-title { font-size: 2em; }
            .event-card { padding: 15px; }
        }
        </style>
        """, unsafe_allow_html=True)

# Streamlit interface
def main():
    add_custom_css()
    create_database_and_tables()

    st.markdown("<h1 class='main-title'>College Event Management System</h1>", unsafe_allow_html=True)

    menu = ["Add Event", "View Events", "Register for Event", "Cancel Registration", "View Event Registrations"]
    choice = st.sidebar.selectbox("Select an option", menu)

    if choice == "Add Event":
        st.subheader("Add New Event")
        event_name = st.text_input("Event Name")
        event_date = st.date_input("Event Date")
        event_time = st.time_input("Event Time")
        venue = st.text_input("Venue")
        description = st.text_area("Description")

        if st.button("Add Event"):
            add_event(event_name, event_date, event_time, venue, description)

    elif choice == "View Events":
        st.subheader("View All Events")
        df_events = view_events()
        
        # Display each event in a card
        for _, row in df_events.iterrows():
            st.markdown(f"""
                <div class="event-card">
                    <div class="event-title">{row['Event Name']}</div>
                    <div class="event-info"><strong>Date:</strong> {row['Event Date']}</div>
                    <div class="event-info"><strong>Time:</strong> {row['Event Time']}</div>
                    <div class="event-info"><strong>Venue:</strong> {row['Venue']}</div>
                    <div class="event-info"><strong>Description:</strong> {row['Description']}</div>
                </div>
            """, unsafe_allow_html=True)

    elif choice == "Register for Event":
        st.subheader("Register for Event")
        student_id = st.text_input("Student ID")
        event_id = st.number_input("Event ID", min_value=1)

        if st.button("Register"):
            register_student(student_id, event_id)

    elif choice == "Cancel Registration":
        st.subheader("Cancel Registration")
        student_id = st.text_input("Student ID")
        event_id = st.number_input("Event ID", min_value=1)

        if st.button("Cancel Registration"):
            cancel_registration(student_id, event_id)

    elif choice == "View Event Registrations":
        st.subheader("View Students Registered for an Event")
        event_id = st.number_input("Enter Event ID", min_value=1)

        if st.button("View Registrations"):
            registrations = view_registrations(event_id)
            if registrations:
                st.write("Registered Students:")
                st.write(registrations)
            else:
                st.write("No students registered for this event.")

if __name__ == "__main__":
    main()
