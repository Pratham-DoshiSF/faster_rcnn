import psycopg2
from psycopg2 import errors
from dotenv import load_dotenv
import os

load_dotenv()

def init_db():
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            host="localhost",
            user=os.getenv("DATABASE_USERNAME"),
            password=os.getenv("DATABASE_PASSWORD")
        )
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        raise

def create_table():
    conn = init_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer (
                customer_id TEXT NOT NULL,
                location_id TEXT NOT NULL,
                top_left TEXT NOT NULL,
                top_right TEXT NOT NULL,
                bottom_right TEXT NOT NULL,
                bottom_left TEXT NOT NULL,
                PRIMARY KEY (customer_id, location_id)
            );
        """)
        conn.commit()
        print("Table created.")
    except Exception as e:
        print("Error creating table:", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()



def insert_cordinates(customer_id, location_id, roi_points):
    if len(roi_points) != 4:
        raise ValueError("roi_points must contain exactly 4 coordinate pairs.")

    conn = init_db()
    cursor = conn.cursor()

    top_left = str(roi_points[0])
    top_right = str(roi_points[1])
    bottom_right = str(roi_points[2])
    bottom_left = str(roi_points[3])

    query = """
        INSERT INTO customer (customer_id, location_id, top_left, top_right, bottom_right, bottom_left)
        VALUES (%s, %s, %s, %s, %s, %s);
    """

    try:
        cursor.execute(query, (
            customer_id,
            location_id,
            top_left,
            top_right,
            bottom_right,
            bottom_left
        ))
        conn.commit()
        print("Data inserted successfully.")
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        print(f"Data already exists for customer {customer_id}, location {location_id}.")
    except Exception as e:
        conn.rollback()
        print("Error during data insertion.")
        raise e
    finally:
        cursor.close()
        conn.close()


def fetch_cordinates(customer_id, location_id):
    conn = init_db()
    cursor = conn.cursor()

    try:
        query = """
            SELECT top_left, top_right, bottom_right, bottom_left
            FROM customer
            WHERE customer_id = %s AND location_id = %s;
        """
        cursor.execute(query, (customer_id, location_id))
        data = cursor.fetchone()

        if data:
            cleaned_data = [tuple(map(int, coord.strip("()").split(","))) for coord in data]
            return cleaned_data
        else:
            print("No data found for the given customer and location.")
            return None
    except Exception as e:
        print("Error fetching coordinates:", e)
        raise
    finally:
        cursor.close()
        conn.close()


def update_cordinates(customer_id, location_id, updated_roi_points):
    if len(updated_roi_points) != 4:
        raise ValueError("updated_roi_points must contain exactly 4 coordinate pairs.")

    conn = init_db()
    cursor = conn.cursor()

    top_left = str(updated_roi_points[0])
    top_right = str(updated_roi_points[1])
    bottom_right = str(updated_roi_points[2])
    bottom_left = str(updated_roi_points[3])

    query = """
        UPDATE customer
        SET
            top_left = %s,
            top_right = %s,
            bottom_right = %s,
            bottom_left = %s
        WHERE customer_id = %s AND location_id = %s;
    """

    try:
        cursor.execute(query, (
            top_left,
            top_right,
            bottom_right,
            bottom_left,
            customer_id,
            location_id
        ))
        conn.commit()
        print("Successfully updated.")
    except Exception as e:
        conn.rollback()
        print("Error during update:", e)
        raise
    finally:
        cursor.close()
        conn.close()

# insert_cordinates

roi_points = [(16, 424), (612, 421), (554, 584), (55, 618)]

# create_table()

# insert_cordinates("1" , "1" , roi_points)

# data = fetch_cordinates("1" , "1")
# print(data)
# print(type(data))

# update_cordinates("1" , "1" , roi_points)