from .models import Event, ConflictRecord

def _minutesOverlap(Astart, Aend, Bstart, Bend):

    overlapStart = max(Astart, Bstart)
    overlapEnd = min(Aend, Bend)

    if overlapEnd <= overlapStart:
        return 0
    return (overlapEnd - overlapStart).total_seconds() / 60.0

def CreateConflictRecord(new_event: Event):
    if not new_event.start_time or not new_event.end_time:
        return
    
    overlap = Event.objects.filter(
        start_time__lt = new_event.end_time,
        end_time__gt=new_event.start_time,
    ).exclude(id=new_event.id)

    for other in overlap:
        if new_event.id < other.id:
            event1 = new_event
            event2 = other
        else:
            event1 = other
            event2 = new_event

        check_overlapping_minutes = _minutesOverlap(event1.start_time, event1.end_time, event2.start_time, event2.end_time)

        ConflictRecord.objects.get_or_create(
            event1=event1,
            event2=event2,
            defaults={"severity": round(check_overlapping_minutes, 1)},
        )