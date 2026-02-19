from .models import Event, ConflictRecord


#return overlap duration in minutes between time intervals
def _minutesOverlap(Astart, Aend, Bstart, Bend):

    overlapStart = max(Astart, Bstart)
    overlapEnd = min(Aend, Bend)

    if overlapEnd <= overlapStart:
        return 0
    return (overlapEnd - overlapStart).total_seconds() / 60.0

# creates conflict recors for new events
def CreateConflictRecord(new_event: Event):
    if not new_event.start_time or not new_event.end_time:
        return
    
    # find events that overlap with the new event
    overlap = Event.objects.filter(
        owner=new_event.owner,
        start_time__lt = new_event.end_time,
        end_time__gt=new_event.start_time,
    ).exclude(id=new_event.id)

    for other in overlap:
        # ensure ordering consistency
        if new_event.id < other.id:
            event1 = new_event
            event2 = other
        else:
            event1 = other
            event2 = new_event

        check_overlapping_minutes = _minutesOverlap(event1.start_time, event1.end_time, event2.start_time, event2.end_time)

        # avoid dupe records
        ConflictRecord.objects.get_or_create(
            event1=event1,
            event2=event2,
            defaults={"severity": round(check_overlapping_minutes, 1)},
        )