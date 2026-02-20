# Testing documentation
### This file shows our testing week by week in the format Week.ItemToTest.TestNumber (x.y.z)
for example, 1.1.2, shows week 1, function e.g. create event, test 2

### Types of Testing Used in order:

Unit testing: testing individual components such as models and validation logic using Django's testing framework

Integration testing: testing interaction between backend, database and frontend

System testing: Testing the whole system

User testing: Testing by external user

User testing: Getting people to test the system
## Week 1
The goal of week 1 was to get the django backend foundation working with the following models/functions:

### 1: Event: 

#### Test 1.1.1: Create event - Unit Test

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


#### Test 1.1.2: Testing different field requirements <br> - Unit Test
Since the minimum needed is title, start and end time, we need to test that event creation works with just the minimal information.
The result:
<img src ="images/Week1/EventMinimalInfoTest.png" width="50%">

This work correctly. 


#### Test 1.1.3: Testing of deletion of events - Unit Test

Next we need to test if deletion of events work: EventDeletion

<img src="images/Week1/EventDeletion.png" width="70%">

Take a look at the green notification. This proves there was an event called Test and it isn't there anymore

next we play around with omitting different unecessary information. for example, excluding location, eventy type, confidence and group at least once.
Similarly to the test where we omitted all unecessary information, they came back positive


### ConflictRecord

#### Test 1.2.1: Model testing (before logic) - Unit Test

Conflict Record is fairly simple to test at the moment as since we only have the model we have to create it ourselves like so:
<img src="images/Week1/EventDeletion.png" width="60%">

The handling logic is not there yet, it is just that the fundamentals exist, so this test is to just make sure we can create the conflict record
You can also delete it as needed

### AlternativeGroup

#### Test 1.3.1: Grouping testing (also before UI logic) - Unit Test

Similar to ConflictRecord, we just need to know the model works. in the following screenshots you can see two groups with different names. One was created via
creation of an event, the other created manually.

<img src="images/Week1/AlternativeGroup.png" width="60%">

This is working correctly and can also be deleted.

## Week 2
In week 2, we wanted to establish Api endpoints for creating, updating, deleting and listing events, as well as adding validation rules and error responses.

The outcome we wanted was essentially to create manual event management via api and that the backend is essentially functional without and UI.

### API endpoints

#### Test 2.1.1: Testing listing of events on api endpoint - Unit Test

Naturally, we will be testing these on the link: http://127.0.0.1:8000/events
this is the api endpoint name we have used. Firstly, we need to check to see if we can see the list of events and POST (create) an event.
So following this link we get the page and we can see the list of events:

<img src ="images/Week2/APIList.png" width="50%">

This is confirmed to work

#### Test 2.1.2: Testing POST (creation of event) - Unit Test

To do this, we have to simply type in information on the POST section and check if its appended:

<img src ="images/Week2/POSTcheck.png" width="50%">

looking at event with id 5 named "POST check", we can see this worked. In the screenshot you can see where we POSTED the information from

#### Test 2.1.3 Testing updating events - Unit Test

Let's choose the event we just created at the following api endpoint http://127.0.0.1:8000/events/5 - the 5 being the id of the event.
Next lets add a location to update it called "School":

<img src ="images/Week2/UpdateCheck.png" width="50%">

As you can see, this works fine

#### Test 2.1.4 Testing deletion of event - Unit Test

By following the same url as before, we will delete event with id 5:

<img src ="images/Week2/DeleteCheck.png" width="50%">

And we are back to where we started in the event list, meaning deletion of events works fine.
That is all the api endpoints tested

### Validation rule testing 

#### Test 2.2.1: tests.py file - Unit Test

For the validation rule testing, we have written code found in code/backend/calendarapp/tests.py
This containts automated unit tests

To run: python manage.py test calendarapp

This file tests that a title must be required, end time is after start time, and that an event can be created with the required details:

<img src ="images/Week2/ValidationCheck.png" width="80%">

## Week 3

In week 3, the goal was to connect the Django backend API to a real user interface so that events could be visually displayed in a calendar instead of only through the admin panel or API endpoints.

The outcome we wanted was to confirm that events created in the backend can be dynamically retrieved and shown on a frontend calendar using FullCalendar.js.

### Frontend Calendar

#### Test 3.1.1: Testing calendar loads and displays events - Integration Test

We created a minimal React frontend using FullCalendar.js, served with react-scripts, which fetches events from the Django API and displays them in a monthly calendar.

The frontend is run using npm start, which starts the React development server at http://localhost:3000, while the Django backend runs at http://127.0.0.1:8000.

If everything works correctly, events stored in the database should appear visually in a monthly calendar.

<img src ="images/Week3/CalendarView.png" width="50%">

As shown above, the calendar successfully loads and displays events from the backend.

#### Test 3.1.2: Testing dynamic updates from backend to frontend - Integration Test

Next, we tested that new events created via the API or Django admin appear automatically in the calendar.

<img src ="images/Week3/NewEventAppears.png" width="50%">

This proves the frontend is dynamically retrieving data from the backend.

And the same for deleting events.

<img src ="images/Week3/DeletedEvent.png" width="50%">

## Week 4

In week 4, the goal was to implement the file upload pipeline in the Django backend. This includes uploading files, storing them, processing them through the ingestion logic, and making the extracted data available.

Our aim was to enable file uploading successfully, store them in the backend, and process them so that extracted data exists in the system.

### File Upload & Ingestion 


#### Test 4.1.1: Testing file upload storage - Integration Test

We test whether files are being stored after upload.
We check if the file appears inside the media folder in the backend, as well as that a corresponding file record exists in the database (via Django admin)

The file appearing in the media directory confirms file storage is working correctly:

<img src="images/Week4/MediaFolderCheck.png" width="50%">

As well as in the database:

<img src="images/Week4/DjangoCheck.png" width="60%">

#### Test 4.1.2: Testing extracted data creation - Integration Test

After confirming the file uploads correctly, we check whether extracted data is created, specifically, we verify that a new ExtractedData entry is created in the system, as well as that the extracted content can be viewed (via API)

<img src="images/Week4/ExtrDataCheck.png" width="50%">

Confirming that the ingestion process works.

#### Test 4.1.3: Testing frontend file ingestion view - Integration Test

We test the frontend view of uploading a file. Specifically that a file can be selected and uploaded, as well as the extracted data can be reviewed in the interface.

<img src="images/Week4/FrontendCheck.png" width="50%">

The extracted information appears on the frontend, confirming that the front- and backend are connected properly.

## Week 5

In week 5, we implemented converting file data into event candidates and allowing the user to validate them before creating real calendar events.

The goal was that the user coul review, edit, approve or reject the data extracted from uploaded files. 

If approved, a real Event is created in the system.

### Event Candidate Extraction

#### Test 5.1.1: Testing candidate creation from extracted data - Integration Test

After uploading a file and confirming ExtractedData exists (Test 4.1.2), we test whether event candidates are automatically generated from the extracted text.

We check that the event is created in the database, contains needed fields (title, start, end, etc.), and confidence score is stored.

<img src="images/Week5/CandidateCreation.png" width="50%">

Confirming that the extracted text was successfully converted into structured event candidates.
This also confirms that candidate approval successfully creates a real calendar event.

### Candidate API Endpoints

#### Test 5.1.2: Testing approve candidate - Integration Test

See Test 5.1.1

#### Test 5.1.3: Testing reject candidate - Integration Test

Rejection works:

<img src="images/Week5/Rejection.png" width="50%">

#### Test 5.1.4: Tesing edit candidate before approval - Integration Test

We test editing a candidate's fields before approving.

<img src="images/Week5/EditApproval.png" width="50%">

This confirms that the final Event matches the updated candidate data

#### Test 5.2.1: Testing validation page - Integration Test

1. Validation page appears:

<img src="images/Week5/ValidationPage.png" width="50%">

2. Rejection of an event does not create the event.

3. The event appears on the calendar after approval: 

<img src="images/Week5/EventFrontend.png" width="50%">

As well as on the backend:

<img src="images/Week5/EventBackend.png" width="50%">


3. Editing an event:

<img src="images/Week5/EditEvent.png" width="50%">

The validation page is fully functional

## Week 6

### Calendar Smart Generation

#### Test 6.1.1: Testing Modal pop up - Unit Test

Upon clicking the "Smart Plan" button, the modal pops up

<img src="images/Week6/SmartModal.png" >

This works

#### Test 6.1.2: Testing Preference field - Unit Test

We need to ensure that all the preference fields work. All checkboxs work and strictness slider. We need to ensure fields with values are defined and can't introduce unexpected inputs.

Unit tests:
rescheduling events, making sure max shift can't be less than 0 or greater than 1440. This works
Use Working hours: Time must be above 0 and less than 24, and start time must be less than end time: This works
Event Buffer: must be greater than 0 and less than 160. This works

#### Test 6.1.3 Generation of Smart Plan Button - Integration test

This is testing the preferences alongside the generation

Upon pressing generate smart plan button, we are presented with our smart plan. This works.
Next we need to check different combinations of preferences to make sure they work.

Unit tests: 
Respect existing events: Accurately chooses events that fit into slots without existing events. The next few tests assume it is on
Allow Rescheduling: Can reschedule some events into gaps as long as they are in the max shift range. This works. Asume off for following tests
Use working Hours and Avoid weekends. This accurately schedules events within hours and avoids weekends.
Event buffer: Adds a buffer of defined length between events
Strictness slider: Accuratel effects score and changes what events are selected based on that

#### Test 6.1.4 Testing Alternative selection - Integration test

Small unit test: Ensure events suggest alternatives

<img src="images/Week6/Alternatives.png" >

It suggests alternatives, and only when rescheduling events is turned on.

Next we need to make sure it actually changes when you click, as you can see when comparing to the previous image, it does.

<img src= "images/Week6/AlternateSelect.png" >

#### Test 6.1.5: Testing application of smart build - Integration Test

When we apply smart build we want our events to display. This works accurately


## Week 7

This week is adding user login / register and a final system test

### User Login / Registration

#### Test 7.1.1 Login and registration page appear upon loading webapp - Unit Test

<img src= "images/Week7/SignIn.png" >
<img src= "images/Week7/Register.png">

This works.

#### Test 7.1.2 Testing Required Fields - Unit Test

Users must not be able to leave register field blanks

<img src= "images/Week7/RegisterBlank.png" >

Password must be at least 8 characters, this works perfectly

Check for valid Login details:

<img src= "images/Week7/SignInValid.png">

#### Test 7.1.3 Test sign in - Integration Test

Upon entering correct details, the system logs the use rin and redirects them to their calendar

#### Test 7.1.4 Test logout button - Integration Test

This button logs the user out and re-directs them back to log in page. It works.

#### Test 7.1.5 Events display per user - Integration test

To test this, we create two accounts, on one, we create an event. Then we logout and sign into another account.
This works.

#### Test 7.2.1 Testing system flow - System Test

With all the components in place, we need to make sure they work. there are three user flows to follow after logging in.

1. Creating / editing events
2. Importing events and applying smart plan
3. logging out

We need to make sure the whole system works together. To do this we sign in, and first import files.
We make sure events get extracted, we can accept, reject or edit, and use the accept all or reject all. Then we do the same and check smart plan generation.
Next we check that all events are registered through accepting, accept all and smart plan.
Next we check that we can edit those events in the calendar view.
Then we check if we can create new events.
Before logging out, we need to check that the displays for each valendar view also work.

Nothing breaks and it seems to work!

#### Test 7.3.1 User Tests

Finally we did user tests. We got users to sit down and explore our software, and see what challenges they had

User 1:
Found it mostly intuitive, but felt some of the UI elements were a little easy to miss.
Thought the calendar could be used well for project management, Schools and families.
Was able to discover almost all components.
Overrall liked the design and functionality.

User 2:
Felt that the user control wasn't intuitive, as they would have liked to be able to go back in certain places without having to move forward.
Found everything fine, except for the smart plan button.
Felt the software was useful.
Proposed the idea of being able to store pdf documents on the web app, as well as being able to convert calendars into pdfs.

User 3:
This user wasn't explained how the system works and was asked to complete the following tasks:

1. Register an account
2. Upload a file (test files were provided)
3. Approve at least one candidate
4. Generate a smart plan
5. Log out

In case of difficulties they could consult the user manual.

They were able to successfully complete registration and login without any help.

Uploading a file was also seemless, and they completed it without errors.

During event validation they understood the UI clearly and were able to intuit the basic functions on their own (accept/edit/reject).

Generating a smart plan was also successful, however due to it being slightly more complex they did have to consult the users manual.
Nonetheless, with the help of the manual they were able to complete this step too.

Finally logging out also went without issue.

Feedback from User 3:
- They were impressed by the smart plan and found it useful
- Found the user manual clear and helpful
- liked the overall design of the project