# Testing documentation
### This file shows our testing week by week in the format Week.ItemToTest.TestNumber (x.y.z)
for example, 1.1.2, shows week 1, function e.g. create event, test 2

## Week 1
The goal of week 1 was to get the django backend foundation working with the following models/functions:

- **1: Event**

Test 1.1.1: on http://localhost:8000/admin we can test it by creating an event. Information to input: <br>
Title: Maths <br>
Start time: 2026-01-29<br>
    Date:2026-01-29<br>
    Time:10<br>
End time: <br>
    Date: 2026-01-29<br>
    Time: 11<br>
Location: Room 14<br>
Event type: School<br>
Confidence: 1<br>
Group: Group 1 - class<br>

In the following screenshot, we can see the test worked:
<img src="images/Week1/EventTest.png" width="80%">


Test 1.1.2 <br>
Since the minimum needed is title, start and end time, we need to test that event creation works with just the minimal information.
The result:
<img src ="images/Week1/EventMinimalInfoTest.png" width="50%">

This work correctly. 


Test 1.1.3 

Next we need to test if deletion of events work: EventDeletion
<img src="images/Week1/EventDeletion.png" width="70%">

Take a look at the green notification. This proves there was an event called Test and it isn't there anymore

next we play around with omitting different unecessary information. for example, excluding location, eventy type, confidence and group at least once.
Similarly to the test where we omitted all unecessary information, they came back positive


- **2: ConflictRecord**

Test 1.2.1

Conflict Record is fairly simple to test at the moment as since we only have the model we have to create it ourselves like so:
<img src="images/Week1/EventDeletion.png" width="60%">

The handling logic is not there yet, it is just that the fundamentals exist, so this test is to just make sure we can create the conflict record
You can also delete it as needed

- **3: AlternativeGroup**

Similar to ConflictRecord, we just need to know the model works. in the following screenshots you can see two groups with different names. One was created via
creation of an event, the other created manually.

<img src="images/Week1/AlternativeGroup.png" width="60%">

This is working correctly and can also be deleted
