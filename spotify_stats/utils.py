def milliseconds_to_hh_mm_ss(milliseconds):
    seconds = int((milliseconds / 1000) % 60)
    seconds = f'0{seconds}' if seconds < 10 else str(seconds)
    minutes = int((milliseconds / (1000 * 60)) % 60)
    minutes = f'0{minutes}' if minutes < 10 else str(minutes)
    hours = int(milliseconds / (1000 * 60 * 60))
    return hours, minutes, seconds
