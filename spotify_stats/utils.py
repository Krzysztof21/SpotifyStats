def convert_millis(millis):
    seconds = int((millis/1000) % 60)
    minutes = int((millis/(1000*60)) % 60)
    hours = int((millis/(1000*60*60)) % 24)
    return hours, minutes, seconds
