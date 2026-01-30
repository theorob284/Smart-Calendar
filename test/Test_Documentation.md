# Testing documentation
### This file shows our testing week by week in the format Week.ItemToTest.TestNumber (x.y.z)
for example, 1.1.2, shows week 1, function e.g. create event, test 2

## Week 1
The goal of week 1 was to get the django backend foundation working with the following models/functions:

### 1: Event

#### Test 1.1.1: Create event 

on http://localhost:8000/admin we can test it by creating an event. Information to input: <br>
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


#### Test 1.1.2: Testing different field requirements <br>
Since the minimum needed is title, start and end time, we need to test that event creation works with just the minimal information.
The result:
<img src ="images/Week1/EventMinimalInfoTest.png" width="50%">

This work correctly. 


#### Test 1.1.3: Testing of deletion of events

Next we need to test if deletion of events work: EventDeletion
<img src="images/Week1/EventDeletion.png" width="70%">

Take a look at the green notification. This proves there was an event called Test and it isn't there anymore

next we play around with omitting different unecessary information. for example, excluding location, eventy type, confidence and group at least once.
Similarly to the test where we omitted all unecessary information, they came back positive


### ConflictRecord

#### Test 1.2.1: Model testing (before logic)

Conflict Record is fairly simple to test at the moment as since we only have the model we have to create it ourselves like so:
<img src="images/Week1/EventDeletion.png" width="60%">

The handling logic is not there yet, it is just that the fundamentals exist, so this test is to just make sure we can create the conflict record
You can also delete it as needed

### AlternativeGroup

#### Test 1.3.1: Grouping testing (also before UI logic)

Similar to ConflictRecord, we just need to know the model works. in the following screenshots you can see two groups with different names. One was created via
creation of an event, the other created manually.

<img src="images/Week1/AlternativeGroup.png" width="60%">

This is working correctly and can also be deleted.

## Week 2
In week 2, we wanted to establish Api endpoints for creating, updating, deleting and listing events, as well as adding validation rules and error responses.

The outcome we wanted was essentially to create manual event management via api and that the backend is essentially functional without and UI.

### API endpoints

#### Test 2.1.1: Testing listing of events on api endpoint

Naturally, we will be testing these on the link: http://127.0.0.1:8000/events
this is the api endpoint name we have used. Firstly, we need to check to see if we can see the list of events and POST (create) an event.
So following this link we get the page and we can see the list of events:

<img src ="images/Week2/APIList.png" width="50%">

This is confirmed to work

#### Test 2.1.2: Testing POST (creation of event)

To do this, we have to simply type in information on the POST section and check if its appended:

<img src ="images/Week2/POSTcheck.png" width="50%">

looking at event with id 5 named "POST check", we can see this worked. In the screenshot you can see where we POSTED the information from

#### Test 2.1.3 Testing updating events

Let's choose the event we just created at the following api endpoint http://127.0.0.1:8000/events/5 - the 5 being the id of the event.
Next lets add a location to update it called "School":

<img src ="images/Week2/UpdateCheck.png" width="50%">

As you can see, this works fine

#### Test 2.1.4 Testing deletion of event

By following the same url as before, we will delete event with id 5:

<img src ="images/Week2/DeleteCheck.png" width="50%">

And we are back to where we started in the event list, meaning deletion of events works fine.
That is all the api endpoints tested

### Validation rule testing

#### Test 2.2.1: tests.py file

For the validation rule testing, we have written code found in code/backend/calendarapp/tests.py

To run: python manage.py test calendarapp

This file tests that a title must be required, end time is after start time, and that an event can be created with the required details:

<img src ="images/Week2/ValidationCheck.png" width="80%">

## Week 3
#### placeholder

