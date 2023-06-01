import pygsheets
import datetime

# Load the credentials from the JSON file
gc = pygsheets.authorize(service_file='service_key_file.json')

# Open the Google Sheet by its title
sheet = gc.open('IDP Group 8: API Coding')

def format_seconds(seconds: int) -> str:
    """Convert time in seconds to following format: hh:mm:ss"""
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    
    # Format the time string
    return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)

def append_data_to_sheet(playerUsername: str, max_time: int, puzzle1Time: int, puzzle2Time: int, puzzle3Time: int, hints: int, hintsUsedPuzzle1: int, hintsUsedPuzzle2: int, hintsUsedPuzzle3: int, hardestPuzzle: str, easiestPuzzle: str, gameRating: str) -> None:
    """Appends relevant data of the game to the given Google Sheet"""
    # Load the credentials from the JSON file
    #gc = pygsheets.authorize(service_file='service_key_file.json')  #Outside of loop so not nessary.

    # Open the Google Sheet by its title
    #sheet = gc.open('IDP Group 8: API Coding')  #Outside of loop so not nessary.

    # Select the first worksheet
    wks1 = sheet[0]
    
    # The max_time is controled (aka consistent)
    max_time = 900
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")
    
    # Prepare the data to be appended
    total_time = puzzle1Time + puzzle2Time + puzzle3Time
    data = [playerUsername, 
            str((max_time - total_time) * 1000), 
            format_seconds(max_time), 
            format_seconds(puzzle1Time), 
            format_seconds(puzzle2Time), 
            format_seconds(puzzle3Time), 
            format_seconds(total_time), 
            str(hints), 
            str(hintsUsedPuzzle1), 
            str(hintsUsedPuzzle2), 
            str(hintsUsedPuzzle3),
            hardestPuzzle, 
            easiestPuzzle, 
            gameRating,
            formatted_datetime]

    # Append the data to the worksheet
    wks1.append_table(start='A1', end=None, values=[data], dimension='ROWS')
    print('Data appended successfully.') #worksheet.get_value([cellname])

def retrieve_data_from_sheet(cellname):
    """Returns a value from sheet 2 when given a cellname"""
    wks2 = sheet[1]
    return wks2.get_value(cellname)