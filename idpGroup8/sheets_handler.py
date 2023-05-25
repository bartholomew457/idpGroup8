import pygsheets

def format_seconds(seconds: int) -> str:
    """Convert time in seconds to following format: hh:mm:ss"""
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    
    # Format the time string
    return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)

def append_data_to_sheet(username: str, max_time: int, time1: int, time2: int, time3: int) -> None:
    """Appends relevant data of the game to the given Google Sheet"""
    # Load the credentials from the JSON file
    gc = pygsheets.authorize(service_file='service_key_file.json')

    # Open the Google Sheet by its title
    sheet = gc.open('IDP Group 8: API Coding')

    # Select the first worksheet
    worksheet = sheet.sheet1

    # Prepare the data to be appended
    total_time = time1 + time2 + time3
    data = [username, max_time - total_time, format_seconds(max_time), format_seconds(time1), format_seconds(time2), format_seconds(time3), format_seconds(total_time)]

    # Append the data to the worksheet
    worksheet.append_table(start='A1', end=None, values=[data], dimension='ROWS')
    print('Data appended successfully.')