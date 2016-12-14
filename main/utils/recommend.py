import datetime

def recommend_uber(info_dict):
    recommend = [False,None,None]
    formatting = '%I:%M%p'

    if info_dict['Uber price'] != 'Directions not found':
        uber_time = info_dict['Uber duration'].split(" ")[0]
        uber_arrival = info_dict['Uber driver arrival (sec)']
        uber_departure = (datetime.datetime.now() + datetime.timedelta(seconds=int(uber_arrival)))

        mbta_time = info_dict['MBTA duration']
        t_depart = info_dict['MBTA depart time']
        t_departure = datetime.datetime.strptime(t_depart, '%I:%M%p')

        # if you have to wait more than 30 minutes for the T, rec an uber
        if ((uber_departure + datetime.timedelta(minutes=30)).time() < t_departure.time()):
            recommend[0] = True
            arrival = (uber_departure).time()
            recommend[1] = "The Uber would arrive at {}, a much shorter wait time than for the T.".format(arrival.strftime(formatting).lower())
        # if the uber gets there before the T even leaves
        if ((uber_departure + datetime.timedelta(minutes=int(uber_time))).time() <= t_departure.time()):
            recommend[0] = True
            arrival = (uber_departure + datetime.timedelta(minutes=int(uber_time))).time()
            recommend[2] = "The Uber would get to your destination at {}, which is before your designated departure time!".format(arrival.strftime(formatting).lower())

    print(recommend)
    return recommend