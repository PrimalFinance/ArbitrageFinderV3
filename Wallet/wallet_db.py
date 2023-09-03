
# Sqlite imports 
import sqlite3

# Import pandas 
import pandas as pd


class WalletDatabase:
    def __init__(self, csv_file: str) -> None:
        # Path to csv file for the specified network.
        self.csv_file = csv_file
        # Parse the network name from the csv path. 
        self.network = self.csv_file.split("\\")[-1].split("_")[0]

        # Connect to database file.
        self.conn = sqlite3.connect("wallet_snapshots.db")
        self.cur = self.conn.cursor()
        print(f"Network: {self.network}")
    '''-----------------------------------'''
    '''-----------------------------------'''
    def create_table(self) -> None:
        """
        Creates a table for the network if it does not exist.
        """
        query = f"""CREATE TABLE IF NOT EXISTS {self.network} (
            date DATE,
            time TIME,
            ticker TEXT,
            balance REAL,
            value TEXT
        );
        """

        # Execute query with the cursor.
        self.cur.execute(query)
        # Save changes made.
        self.conn.commit()
    '''-----------------------------------'''
    def upload_snapshot(self) -> None:
        """
        Reads the current data from the csv file and inserts the data to the database.
        """
        # Read the csv data.
        csv_file = pd.read_csv(self.csv_file)

        for index, row in csv_file.iterrows():
            try:
                print(f"Row: {row['date']} {row['time']} {row['ticker']}")
                query = f"SELECT * FROM `{self.network}` WHERE `date` = ? AND `time` = ? AND `ticker` = ?"
                existing_record = self.cur.execute(query, (row["date"], row["time"], row["ticker"])).fetchone()

                # If there is no record with a matching time and date for the specified ticker. 
                if not existing_record:
                    insert_query = f"INSERT INTO {self.network} VALUES (?,?,?,?,?)"
                    self.cur.execute(insert_query, row)
            # Occurs if a table has not been created for the network.
            except sqlite3.OperationalError:
                # Create a table if one does not exist.
                self.create_table()
                query = f"SELECT * FROM {self.network} WEHRE date = {row['date']} AND time = {row['time']} and ticker = {row['ticker']}"
                existing_record = self.cur.execute(query, (row["date"], row["time"], row["ticker"])).fetchone()

                # If there is no record with a matching time and date for the specified ticker. 
                if not existing_record:
                    insert_query = f"INSERT INTO {self.network} VALUES (?,?,?,?,?)"
                    self.cur.execute(insert_query, row)

        
        # Save inserts made.
        self.conn.commit()
        self.conn.close()

    '''-----------------------------------'''
    def get_snapshots(self):
        """
        Gets the snapshots from the database.
        """
        # Query to get snapshots.
        query = f"SELECT * FROM {self.network}"
        # Execute query.
        self.cur.execute(query)
        # Fetch all the rows from the executed query.
        snapshots = self.cur.fetchall()

        snapshot_dict = {
            "Snapshot_1": {}
        }

        index = 0
        snapshot_index = 1
        for snap in snapshots:
            snapshot_key = f"Snapshot_{snapshot_index}"
            date, time, ticker, balance, value = snap

            if index == 0:
                snapshot_dict[snapshot_key] = [{
                    "date": date,
                    "time": time,
                    "ticker": ticker,
                    "balance": balance,
                    "value": value
                }]
            else:
                # Get the previous snapshot. 
                prev_snap = snapshots[index-1] 
                prev_date, prev_time, prev_ticker, prev_balance, prev_value = prev_snap

                # If the date & time matches the previous entry, then they are part of the same snapshot.
                if date == prev_date and time == prev_time:


                    if snapshot_key not in snapshot_dict:
                        snapshot_dict[snapshot_key] = [{
                            "date": date,
                            "time": time,
                            "ticker": ticker,
                            "balance": balance,
                            "value": value
                        }]
                    else:

                        snapshot_dict[snapshot_key].append({
                            "date": date,
                            "time": time,
                            "ticker": ticker,
                            "balance": balance,
                            "value": value
                        })
                # If the date and time do not match the previous row.  
                else:
                    snapshot_index += 1
                    snapshot_key = f"Snapshot_{snapshot_index}"
                    snapshot_dict[snapshot_key] = [{
                        "date": date,
                        "time": time,
                        "ticker": ticker,
                        "balance": balance,
                        "value": value
                    }]


            index += 1 
        return snapshot_dict
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''