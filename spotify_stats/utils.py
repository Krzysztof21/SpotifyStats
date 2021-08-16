def convert_millis(millis):
    seconds = int((millis/1000) % 60)
    seconds = f'0{seconds}' if seconds < 10 else str(seconds)
    minutes = int((millis/(1000*60)) % 60)
    minutes = f'0{minutes}' if minutes < 10 else str(minutes)
    hours = int(millis/(1000*60*60))
    return hours, minutes, seconds
