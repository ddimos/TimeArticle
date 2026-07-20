from datetime import datetime, timedelta
import calendar
import matplotlib.pyplot as plt
import numpy as np

def parse(file_path):
    days = []
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            parts = line.split()
            dateStr = parts[0]
            timestamps = parts[1].split('-')
            realDurationStr = parts[2].strip('~')

            timeStart = datetime.strptime(timestamps[0], "%H:%M").time()
            timeEnd = datetime.strptime(timestamps[1], "%H:%M").time()
            date = datetime.strptime(dateStr, "%d.%m.%y")

            dateTimeStart = datetime.combine(date=date, time=timeStart)
            dateTimeEnd = datetime.combine(date=date, time=timeEnd)
            isTheSameDay = True
            if timeEnd < timeStart:
                dateTimeEnd = dateTimeEnd + timedelta(days=1)
                isTheSameDay = False

            realDuration = 0
            if realDurationStr.endswith("h"):
                realDuration = float(realDurationStr[:-1]) * 3600
            elif realDurationStr.endswith("m"):
                realDuration = float(realDurationStr[:-1]) * 60
            else:
                raise ValueError(f"Invalid duration: {realDurationStr}")
        
            days.append((dateTimeStart, dateTimeEnd, isTheSameDay, dateTimeStart.weekday(), realDuration))

    return days

def calculatePerDay(days):
    perDay = {}
    for i, (dateTimeStart, dateTimeEnd, isTheSameDay, weekday, realDuration) in enumerate(days):
        durationSeconds = 0
        startDate = dateTimeStart.date()
        endDate = dateTimeEnd.date()

        if perDay.get(startDate) is None:
            perDay[startDate] = 0

        if isTheSameDay:
            durationSeconds = (dateTimeEnd - dateTimeStart).total_seconds()
            perDay[startDate] += durationSeconds
        else:
            startOfNextDay = dateTimeEnd.replace(hour=0, minute=0, second=0, microsecond=0)

            secondsUntilEnd = (startOfNextDay - dateTimeStart).total_seconds()
            secondsSinceStart = (dateTimeEnd - startOfNextDay).total_seconds()

            perDay[startDate] += secondsUntilEnd
            if secondsSinceStart > 0:
                if perDay.get(endDate) is None:
                    perDay[endDate] = 0
                perDay[endDate] += secondsSinceStart
        
    return perDay

def calculateStats(perDay, days):
    total = 0

    perDaySorted = sorted(
        (d, secs)
        for d, secs in perDay.items()
    )

    perDurationSorted = sorted(
        (secs, d)
        for d, secs in perDay.items()
    )
    firstDate = perDaySorted[0][0]
    lastDate = perDaySorted[len(perDay)-1][0]
    duration = lastDate-firstDate
    print(f"First day: {firstDate}, Last day: {lastDate}, Duration: {duration.days} days")

    count = 0
    for i, (date, seconds) in enumerate(perDaySorted):
        total += seconds
        count += 1

    print("Unique days:", len(perDaySorted))

    print(f"Total time: {total} s, {total/3600} h")
    print(f"Average per day: {(total/count)/3600} hours")
   
    print(f"The shortest day {perDurationSorted[0][1]}, {perDurationSorted[0][0]} s") 
    print(f"The longest day {perDurationSorted[len(perDurationSorted)-1][1]}, {perDurationSorted[len(perDurationSorted)-1][0]/3600} h") 
    total = 0
    count = 0
    realTotal = 0
    min = 3600
    max = 0
    for i, (dateTimeStart, dateTimeEnd, isTheSameDay, weekday, realDuration) in enumerate(days):
        sec = (dateTimeEnd - dateTimeStart).total_seconds()
        total += sec
        count += 1
        realTotal += realDuration
        if sec > max:
            max = sec
        if sec < min:
            min = sec

    hours = int(realTotal // 3600)
    minutes = int((realTotal % 3600)/60)

    print(f"Average per session: {(total/count)/3600} hours, sessions: {count}")
    print(f"The shortest session {min} s") 
    print(f"The longest session {max/3600} h")

    print(f"Total real time: {hours}h {minutes}m")

def plotHeatmap(perDay):
    perDaySorted = {
        date: seconds / 3600
        for date, seconds in perDay.items()
    }
    startDate = min(perDaySorted)
    endDate = max(perDaySorted)

    dates = []
    hours = []

    currentDate = startDate
    while currentDate <= endDate:
        dates.append(currentDate)
        hours.append(perDaySorted.get(currentDate, 0))
        currentDate += timedelta(days=1)

    weeks = (len(hours) + 6) // 7
    daysY = []

    heatmap = np.zeros((7, weeks))

    prevMonth = 0
    for i, value in enumerate(hours):
        week = i // 7
        day = i % 7
        if day == 0:
            if prevMonth != dates[i].month:
                daysY.append(" ".join([calendar.month_abbr[dates[i].month], dates[i].strftime("%y")]))
            else:
                daysY.append(" ")
            prevMonth = dates[i].month
        heatmap[day, week] = value

    plt.figure(figsize=(12, 4))
    plt.imshow(heatmap, cmap="viridis", aspect="auto")

    plt.colorbar(label="Hours")
    plt.xticks(range(weeks), [f"{daysY[i]}" for i in range(weeks)], rotation=20)
    plt.yticks(
        range(7),
        calendar.day_abbr
    )

    plt.title("Daily Activity")
    plt.show()

def plotPerDay(perDay):
    startDate = min(perDay)
    endDate = max(perDay)

    counts = []
    dates = []
    hours = []
    hoursCumulative = []

    currentDate = startDate
    cumulative = 0
    i = 0
    prevMonth = 0
    while currentDate <= endDate:
        counts.append(i)

        duration = perDay.get(currentDate, 0) / 3600
        hours.append(duration)
        
        day = i % 7
        if day == 0:
            if prevMonth != currentDate.month:
                dates.append(" ".join([calendar.month_abbr[currentDate.month], currentDate.strftime("%y")]))
            else:
                dates.append(" ")
            prevMonth = currentDate.month
        cumulative += duration
        hoursCumulative.append(cumulative)
        currentDate += timedelta(days=1)
        i += 1

    dates.append(" ")

    # Linear
    plt.figure(figsize=(10, 5))
    plt.plot(counts, hours)
    plt.fill_between(counts, hours)
    plt.xlabel("Date")
    plt.ylabel("Hours")
    plt.title("Daily Work Time")
    plt.ylim(0, 7)
    plt.xlim(counts[0], counts[len(counts)-1])
    plt.xticks(range(0, 442, 7), [f"{dates[i]}" for i in range(64)], rotation=20)
    plt.tight_layout()
    plt.show()

    # Cumulative
    plt.figure(figsize=(10, 5))
    plt.plot(counts, hoursCumulative)
    plt.fill_between(counts, hoursCumulative)
    plt.ylabel("Hours")
    plt.title("Cumulative Work Time")
    plt.ylim(0, 410)
    plt.xlim(counts[0], counts[len(counts)-1])
    plt.xticks(range(0, 442, 7), [f"{dates[i]}" for i in range(64)], rotation=20)
    plt.tight_layout()
    plt.show()
    
def plotByWeek(perDay):
    startDate = min(perDay)
    endDate = max(perDay)

    perWeek = {}

    currentDate = startDate
    while currentDate <= endDate:
        weekAndYear = currentDate.isocalendar()[:2]
        if perWeek.get(weekAndYear) is None:
            perWeek[weekAndYear] = 0
        perWeek[weekAndYear] += perDay.get(currentDate, 0)

        currentDate += timedelta(days=1)
    
    x = [d for d in perWeek]
    y = [secs for _, secs in perWeek.items()] 

    plt.figure(figsize=(10, 5))
    plt.plot( [f"{y}-{w}" for y, w in x], y, marker="o")
    plt.xlabel("Date")
    plt.ylabel("Hours spent")
    plt.title("Hours spent per week")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plotByMonth(perDay):
    perDaySorted = sorted(
        (d, secs)
        for d, secs in perDay.items()
    )
        
    perMonth = {}
    for date, seconds in perDaySorted:
        monthAndYear = date.strftime("%m.%y")
        if perMonth.get(monthAndYear) is None:
            perMonth[monthAndYear] = 0
            if monthAndYear == "08.25":
                perMonth["09.25"] = 0
                
        perMonth[monthAndYear] += seconds
    
    x = [d for d in perMonth]
    y = [secs / 3600 for _, secs in perMonth.items()]

    plt.figure(figsize=(10, 5))
    plt.plot(x, y, marker="o")
    plt.xlabel("Date")
    plt.ylabel("Hours spent")
    plt.title("Hours spent per month")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plotTotalTimePerDay(perDay):
    durationCounts = [0, 0, 0, 0, 0, 0, 0]
    for date, seconds in perDay.items():
        if seconds < 1800:
            durationCounts[0] += 1
        elif seconds >= 1800 and seconds < 3600:
            durationCounts[1] += 1
        elif seconds >= 3600 and seconds < 7200:
            durationCounts[2] += 1
        elif seconds >= 7200 and seconds < 10800:
            durationCounts[3] += 1
        elif seconds >= 10800 and seconds < 14400:
            durationCounts[4] += 1
        elif seconds >= 14400 and seconds < 18000:
            durationCounts[5] += 1
        else:
            durationCounts[6] += 1
    labels = ["<30m", "[30m-1h)", "[1-2h)", "[2-3h)", "[3-4h)", "[4-5h)", ">5h"]

    plt.bar(labels, durationCounts)
    plt.xlabel("Time")
    plt.ylabel("Frequency")
    plt.title("Daily Total Work Time")
    plt.show()

def plotAverageTimePerDayOfWeek(perDay):
    average = {}
    for date, seconds in perDay.items():
        if average.get(date.weekday()) is None:
            average[date.weekday()] = {"total":0.0, "count":0}
        average[date.weekday()]["total"] += seconds
        average[date.weekday()]["count"] += 1

    labels = calendar.day_abbr
    values = [(average[i]["total"]/average[i]["count"])/3600 for i in range(7)]
    
    plt.bar(labels, values)
    plt.xlabel("Day of week")
    plt.ylabel("Hours")
    plt.title("Average Time by Day of Week")
    plt.show()

def plotFrequencyByDayOfWeek(perDay):
    weekdayCounts = {}
    for date, seconds in perDay.items():
        if weekdayCounts.get(date.weekday()) is None:
            weekdayCounts[date.weekday()] = 0
        weekdayCounts[date.weekday()] += 1

    labels = calendar.day_abbr
    values = [weekdayCounts[i] for i in range(7)]

    plt.bar(labels, values)
    plt.xlabel("Day of week")
    plt.ylabel("Number of days")
    plt.title("Frequency by Day of Week")
    plt.show()

def plotTotalTimePerDayOfWeek(perDay):
    total = {}
    for date, seconds in perDay.items():
        if total.get(date.weekday()) is None:
            total[date.weekday()] = {"total":0.0}
        total[date.weekday()]["total"] += seconds

    labels = calendar.day_abbr
    values = [(total[i]["total"])/3600 for i in range(7)]
    
    plt.bar(labels, values)
    plt.xlabel("Day of week")
    plt.ylabel("Hours")
    plt.title("Total Time by Day of Week")
    plt.show()

def plotTotalTimeVSDayOfWeekHeatmap(perDay):
    x = []
    y = []
    for date, seconds in perDay.items():
        x.append(seconds/3600)
        y.append(date.weekday())

    fig, ax = plt.subplots()

    ax.set_yticks(np.arange(0.5, 7, 1))
    ax.set_yticklabels(calendar.day_abbr)

    hist = ax.hist2d(x,y, bins=(np.arange(0, 8, 0.5), np.arange(0, 8, 1)))
    
    cbar = fig.colorbar(hist[3], ax=ax)
    cbar.set_label("Frequency")
    plt.title("Total Time by Day of Week")
    plt.xlabel("Hours")
    plt.ylabel("Day of week")
    plt.show()

def plotNumberOfSessionsPerDay(days):
    perDay = {}
    for i, (dateTimeStart, dateTimeEnd, isTheSameDay, weekday, realDuration) in enumerate(days):
        if perDay.get(dateTimeStart.date()) is None:
            perDay[dateTimeStart.date()] = 0
        perDay[dateTimeStart.date()] +=1

    sessions = [0]*7
    for date, numberOfSessions in perDay.items():
        sessions[numberOfSessions-1] += 1

    plt.bar([1,2,3,4,5,6,7], sessions)
    plt.xlabel("Number of activities")
    plt.ylabel("Number of days")
    plt.title("Activities per Day")
    plt.show()

def plotTotalNumberOfActivitiesVSDayOfWeek(days):
    perDay = {}
    for i, (dateTimeStart, dateTimeEnd, isTheSameDay, weekday, realDuration) in enumerate(days):
        if perDay.get(dateTimeStart.date().weekday()) is None:
            perDay[dateTimeStart.date().weekday()] = 0
        perDay[dateTimeStart.date().weekday()] +=1

    labels = calendar.day_abbr
    values = [perDay[i] for i in range(7)]

    plt.bar(labels, values)
    plt.xlabel("Day of week")
    plt.ylabel("Number of activities")
    plt.title("Activity Count by Day of Week")
    plt.show()

def plotActivityCountVSDayOfWeek(days):
    perDay = {}
    for i, (dateTimeStart, dateTimeEnd, isTheSameDay, weekday, realDuration) in enumerate(days):
        if perDay.get(dateTimeStart.date()) is None:
            perDay[dateTimeStart.date()] = 0
        perDay[dateTimeStart.date()] +=1

    x = []
    y = []
    for date, numberOfSessions in perDay.items():
        x.append(numberOfSessions)
        y.append(date.weekday())

    fig, ax = plt.subplots()

    ax.set_yticks(np.arange(0.5, 7, 1))
    ax.set_yticklabels(calendar.day_abbr)

    hist = ax.hist2d(x,y, bins=(np.arange(1, 8, 1), np.arange(0, 8, 1)))
    
    cbar = fig.colorbar(hist[3], ax=ax)
    cbar.set_label("Frequency")
    plt.title("Activity Count by Day of Week")
    plt.xlabel("Activity Count")
    plt.ylabel("Day of week")
    plt.show()

def plotDurationOfOneSession(days):
    durationCounts = [0, 0, 0, 0, 0, 0, 0]
    for i, (dateTimeStart, dateTimeEnd, isTheSameDay, weekday, realDuration) in enumerate(days):
        seconds = (dateTimeEnd - dateTimeStart).total_seconds()
        if seconds < 1800:
            durationCounts[0] += 1
        elif seconds >= 1800 and seconds < 3600:
            durationCounts[1] += 1
        elif seconds >= 3600 and seconds < 7200:
            durationCounts[2] += 1
        elif seconds >= 7200 and seconds < 10800:
            durationCounts[3] += 1
        elif seconds >= 10800 and seconds < 14400:
            durationCounts[4] += 1
        elif seconds >= 14400 and seconds < 18000:
            durationCounts[5] += 1
        else:
            durationCounts[6] += 1
    labels = ["<30m", "[30m-1h)", "[1-2h)", "[2-3h)", "[3-4h)", "[4-5h)", ">5h"]

    plt.bar(labels, durationCounts)
    plt.xlabel("Duration")
    plt.ylabel("Frequency")
    plt.title("Activity Duration")
    plt.show()

def plotActivityDurationVSDayOfWeek(days): 
    x = []
    y = []
    for i, (dateTimeStart, dateTimeEnd, isTheSameDay, weekday, realDuration) in enumerate(days):
        durationSeconds = (dateTimeEnd - dateTimeStart).total_seconds()
        x.append(durationSeconds/3600)
        y.append(weekday) # What should I do when isTheSameDay == false

    fig, ax = plt.subplots()

    ax.set_yticks(np.arange(0.5, 7, 1))
    ax.set_yticklabels(calendar.day_abbr)

    hist = ax.hist2d(x,y, bins=(np.arange(0, 8, 0.5), np.arange(0, 8, 1)))
    
    cbar = fig.colorbar(hist[3], ax=ax)
    cbar.set_label("Frequency")
    plt.title("Activity Duration by Day of Week")
    plt.xlabel("Duration, h")
    plt.ylabel("Day of week")
    plt.show()

def plotStartEndTimeHist(days):
    startEndTimeCounts = []

    for i, (dateTimeStart, dateTimeEnd, isTheSameDay, weekday, realDuration) in enumerate(days):
        startEndTimeCounts.append([dateTimeStart.time().hour, dateTimeEnd.time().hour])

    startEndTimeCounts = np.array(startEndTimeCounts)

    # plot:
    fig, ax = plt.subplots()
    ax.hist(
        startEndTimeCounts,
        bins=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],
        edgecolor="white",
        align="left",
        label=["Start time", "End time"])

    ax.legend(prop={'size': 10})
    ax.set(xlim=(-1, 24), xticks=np.arange(0, 24))

    plt.title("Activity Start and End Time")
    plt.xlabel("Time of day")
    plt.ylabel("Frequency")

    plt.show()

def plotStartTime(days):
    startTimeCounts = [0] * 24
    for i, (dateTimeStart, dateTimeEnd, isTheSameDay, weekday, realDuration) in enumerate(days):
        startTimeCounts[dateTimeStart.time().hour] += 1

    labels = list(range(24))

    plt.bar(labels, startTimeCounts)
    plt.xlabel("Start Time")
    plt.ylabel("Count")
    plt.title("Start Time count")
    plt.show()

def plotEndTime(days):
    endTimeCounts = [0] * 24
    for i, (dateTimeStart, dateTimeEnd, isTheSameDay, weekday, realDuration) in enumerate(days):
        endTimeCounts[dateTimeEnd.time().hour] += 1

    labels = list(range(24))

    plt.bar(labels, endTimeCounts)
    plt.xlabel("End Time")
    plt.ylabel("Count")
    plt.title("End Time count")
    plt.show()

def plotStartEndVSDayOfWeek(days):

    xSt = []
    ySt = []
    for i, (dateTimeStart, dateTimeEnd, isTheSameDay, weekday, realDuration) in enumerate(days):
        xSt.append(dateTimeStart.hour + dateTimeStart.minute/60)
        ySt.append(weekday+1.1)

    xEn = []
    yEn = []
    for i, (dateTimeStart, dateTimeEnd, isTheSameDay, weekday, realDuration) in enumerate(days):
        xEn.append(dateTimeEnd.hour + dateTimeEnd.minute/60)
        yEn.append(weekday+0.9)

    fig, ax = plt.subplots()

    ax.scatter(xSt, ySt)
    ax.scatter(xEn, yEn)

    ax.set(xlim=(0, 24), xticks=np.arange(1, 24))

    ax.set_yticks([1, 2, 3, 4, 5, 6, 7])
    ax.set_yticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])

    plt.show()

def plotStartTimeVSDayOfWeek(days):
    x = []
    y = []

    for i, (dateTimeStart, dateTimeEnd, isTheSameDay, weekday, realDuration) in enumerate(days):
        x.append(dateTimeStart.time().hour)
        y.append(weekday)

    fig, ax = plt.subplots(figsize=(9, 5))

    ax.set_xticks(np.arange(0, 24, 1))
    ax.set_yticks(np.arange(0.5, 7, 1))
    ax.set_yticklabels(calendar.day_abbr)

    hist = ax.hist2d(x,y, bins=(np.arange(0, 25, 1), np.arange(0, 8, 1)))

    cbar = fig.colorbar(hist[3], ax=ax)
    cbar.set_label("Frequency")

    plt.title("Activity Start Time by Day of Week")
    plt.xlabel("Time of day")
    plt.ylabel("Day of week")
    plt.show()

    # plot by the earliest time if there are two activities
    # startTimePerDay = {}

    # for i, (dateTimeStart, dateTimeEnd, isTheSameDay, weekday, realDuration) in enumerate(days):
    #     date = dateTimeStart.date()
    #     if startTimePerDay.get(date) is None:
    #         startTimePerDay[date] = dateTimeStart.time()
    #     else:
    #         if startTimePerDay[date] > dateTimeStart.time():
    #             startTimePerDay[date] = dateTimeStart.time()

    # x = []
    # y = []
    # for date, timeStart in startTimePerDay.items():
    #     x.append(timeStart.hour)
    #     y.append(date.weekday())

    # fig, ax = plt.subplots(figsize=(9, 5))

    # ax.set_xticks(np.arange(0, 24, 1))
    # ax.set_yticks(np.arange(0.5, 7, 1))#[0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5])
    # ax.set_yticklabels(calendar.day_abbr)

    # hist = ax.hist2d(x,y, bins=(np.arange(0, 25, 1), np.arange(0, 8, 1)))

    # cbar = fig.colorbar(hist[3], ax=ax)
    # cbar.set_label("Activity Count")

    # plt.title("Start Time by Weekday")
    # plt.xlabel("Time of day")
    # plt.ylabel("Day of week")
    # plt.show()

def plotEndTimeVSDayOfWeek(days):
    x = []
    y = []

    for i, (dateTimeStart, dateTimeEnd, isTheSameDay, weekday, realDuration) in enumerate(days):
        x.append(dateTimeEnd.time().hour)
        y.append(dateTimeEnd.weekday())

    fig, ax = plt.subplots(figsize=(9, 5))

    ax.set_xticks(np.arange(0, 24, 1))
    ax.set_yticks(np.arange(0.5, 7, 1))
    ax.set_yticklabels(calendar.day_abbr)

    hist = ax.hist2d(x,y, bins=(np.arange(0, 25, 1), np.arange(0, 8, 1)))

    cbar = fig.colorbar(hist[3], ax=ax)
    cbar.set_label("Frequency")

    plt.title("Activity End Time by Day of Week")
    plt.xlabel("Time of day")
    plt.ylabel("Day of week")
    plt.show()

def plotTimeOfWorkingPerDayOfWeek(days):
    x = []
    y = []

    for i, (dateTimeStart, dateTimeEnd, isTheSameDay, weekday, realDuration) in enumerate(days):
        if isTheSameDay and dateTimeStart.hour == dateTimeEnd.hour:
            x.append(dateTimeStart.hour)
            y.append(weekday)

        currentDate = dateTimeStart
        while currentDate <= dateTimeEnd:

            x.append(currentDate.time().hour)
            y.append(currentDate.weekday())

            currentDate += timedelta(hours=1)

    fig, ax = plt.subplots(figsize=(9, 5))

    ax.set_xticks(np.arange(0, 24, 1))
    ax.set_yticks(np.arange(0.5, 7, 1))
    ax.set_yticklabels(calendar.day_abbr)

    hist = ax.hist2d(x,y, bins=(np.arange(0, 25, 1), np.arange(0, 8, 1)))

    cbar = fig.colorbar(hist[3], ax=ax)
    cbar.set_label("Frequency")

    plt.title("Work Time by Day of Week")
    plt.xlabel("Time of day")
    plt.ylabel("Day of week")
    plt.show()

def plotTimeForTheWholeDuration(days):
    x = []
    y = []

    firstDay = days[len(days)-1][0] # TODO A bit risky to do it without sorting
    for i, (dateTimeStart, dateTimeEnd, isTheSameDay, weekday, realDuration) in enumerate(days):
        if isTheSameDay and dateTimeStart.hour == dateTimeEnd.hour:
            dt = dateTimeStart-firstDay
            x.append(dt.days)
            y.append(dateTimeStart.hour)

        currentDate = dateTimeStart
        while currentDate <= dateTimeEnd:
            dt = currentDate-firstDay
            x.append(dt.days)
            y.append(currentDate.time().hour)

            currentDate += timedelta(hours=1)

    dates = []
    currentDate = firstDay
    i = 0
    prevMonth = 0
    while currentDate <= days[0][0]:
        day = i % 7
        if day == 0:
            if prevMonth != currentDate.date().month:
                dates.append(" ".join([calendar.month_abbr[currentDate.date().month], currentDate.date().strftime("%y")]))
            else:
                dates.append(" ")
            prevMonth = currentDate.date().month

        currentDate += timedelta(days=1)
        i += 1

    fig, ax = plt.subplots(figsize=(9, 5))

    hist = ax.hist2d(x,y,bins=(np.arange(0, 441, 7), np.arange(0, 25, 1)))

    plt.xticks(range(0, 441, 7), [f"{dates[i]}" for i in range(63)], rotation=20)

    cbar = fig.colorbar(hist[3], ax=ax)
    cbar.set_label("Frequency")

    plt.title("Work Schedule by Week")
    plt.ylabel("Time of day")
    plt.show()

def plotDurationVSRealDuration(days):
    durationCounts = [0, 0, 0, 0, 0, 0, 0]
    for i, (dateTimeStart, dateTimeEnd, isTheSameDay, weekday, realDuration) in enumerate(days):
        seconds = (dateTimeEnd - dateTimeStart).total_seconds()
        diff = 0
        if seconds > realDuration:
            diff = seconds - realDuration
        else:
            diff = realDuration - seconds 
        if diff == 0:
            durationCounts[0] += 1
        elif diff < 1800:
            durationCounts[1] += 1
        elif diff >= 1800 and diff < 3600:
            durationCounts[2] += 1
        elif diff >= 3600 and diff < 7200:
            durationCounts[3] += 1
        elif diff >= 7200 and diff < 10800:
            durationCounts[4] += 1
        elif diff >= 10800 and diff < 14400:
            durationCounts[5] += 1
        else:
            durationCounts[6] += 1
    labels = ["0", "<30m", "[30m-1h)", "[1-2h)", "[2-3h)", "[3-4h)", ">4h"]

    plt.bar(labels, durationCounts)
    plt.xlabel("Time difference")
    plt.ylabel("Frequency")
    plt.title("Tracked vs Estimated Work Time")
    plt.show()

# ---------------

days = parse("../data/data")
perDay = calculatePerDay(days)

# calculateStats(perDay, days)

# 1.1
# plotHeatmap(perDay)
# 1.2
# plotPerDay(perDay)
# -
# plotByWeek(perDay)
# -
# plotByMonth(perDay)

# 2.1
# plotTotalTimePerDay(perDay)
# 2.2
# plotAverageTimePerDayOfWeek(perDay)
# 2.3
# plotFrequencyByDayOfWeek(perDay)
# 2.4 
# plotTotalTimePerDayOfWeek(perDay)
# 2.5 
# plotTotalTimeVSDayOfWeekHeatmap(perDay)

# 3.1
# plotNumberOfSessionsPerDay(days)
# 3.2
# plotTotalNumberOfActivitiesVSDayOfWeek(days)
# 3.3
# plotActivityCountVSDayOfWeek(days)
# 3.4
# plotDurationOfOneSession(days)
# 3.5
# plotActivityDurationVSDayOfWeek(days)

# 4.1
# plotStartEndTimeHist(days)
# -
# plotStartTime(days)
# -
# plotEndTime(days)
# -
# plotStartEndVSDayOfWeek(days)
# 4.2
# plotStartTimeVSDayOfWeek(days)
# 4.3
# plotEndTimeVSDayOfWeek(days)
# 4.4
# plotTimeOfWorkingPerDayOfWeek(days)
# 4.5
# plotTimeForTheWholeDuration(days)

# 5.1
# plotDurationVSRealDuration(days)
