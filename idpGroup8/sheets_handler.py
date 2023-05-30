import pygsheets

def format_seconds(seconds: int) -> str:
    """Convert time in seconds to following format: hh:mm:ss"""
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    
    # Format the time string
    return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)

def append_data_to_sheet(playerUsername: str, max_time: int, puzzle1Time: int, puzzle2Time: int, puzzle3Time: int, hints: int, hintsUsedPuzzle1: int, hintsUsedPuzzle2: int, hintsUsedPuzzle3: int, hardestPuzzle: str, easiestPuzzle: str, gameRating: str) -> None:
    """Appends relevant data of the game to the given Google Sheet"""
    # Load the credentials from the JSON file
    gc = pygsheets.authorize(service_file='service_key_file.json')

    # Open the Google Sheet by its title
    sheet = gc.open('IDP Group 8: API Coding')

    # Select the first worksheet
    worksheet = sheet.sheet1
    
    # The max_time is controled (aka consistent)
    max_time = 900
    # Prepare the data to be appended
    total_time = puzzle1Time + puzzle2Time + puzzle3Time
    data = [playerUsername, 
            max_time - total_time, 
            format_seconds(max_time), 
            format_seconds(puzzle1Time), 
            format_seconds(puzzle2Time), 
            format_seconds(puzzle3Time), 
            format_seconds(total_time), 
            hints, 
            hintsUsedPuzzle1, 
            hintsUsedPuzzle2, 
            hintsUsedPuzzle3,
            hardestPuzzle, 
            easiestPuzzle, 
            gameRating]

    # Append the data to the worksheet
    worksheet.append_table(start='A1', end=None, values=[data], dimension='ROWS')
    print('Data appended successfully.')