# User Interface Manual

### We decided to follow Jakob Nielsen's 10 usability principles for user interface design

Nielsen's principles best suited our project, as we felt with a calendar, a simple/minimalist design was important, with major considerations to the data being sent and pulled from the backend.

His 10 principles are:
1. Visibility of System Status
2. Match Between the System and the Real World
3. User Control and Freedom
4. Consistency and Standards
5. Error Prevention
6. Recognition Rather than Recall
7. Flexibility and Efficiency of Use
8. Aesthetic and Minimalist Design
9. Help Users Recognize, Diagnose, and Recover from Errors
10. Help and Documentation


---

## Below we explain how our UI adheres to these rules

**1. Visibility of System Status:**

Our system relies on sending and pulling from a database. With this in mind, visibility of system status is a major design consideration. Users need to be able to use our calendar and know exactly where they are in the user flow. As a result, our system was designed to be fairly intuitive. Users know when they are on the calendar page, when they are creating an event, editing an event, importing an event, checking important events and using the smart generation system. 

On top of that, we have to consider aspects such as conflict detection. In the event that two events overlap, the system instead of ignoring the issue, creates a conflict record that links the two conflicting events and stores needed information (severity and creation time). Instead of leaving overlaps hidden in the schedule, the system formally records them so that they can be identified, displayed and or managed. Even though the interface is simple, the underlying logic clearly tracks scheduling problems, and informs the user about it.

**2. Match Between the System and the Real World**

Fortunately, our system follows a similar format to other existing calendars, so many aspects of it don't need explanation. However, this doesn't mean there are places where we need to pay close attention to the terms and UI design that allow users to relate back to the real world. Our most prominent issue would lie in the smart generation page, where users have preferences to generate their calendar. This is what makes our calendar unique, and so users may not have seen a format like it before. So we have to make sure our language is clear, like in the preference where we allow users to modify time shift, we mention this is in minutes, same with event buffers. The strictness slider language needed to explain what each preference meant, such as light, balanced or strict scheduling.

Icons such as selecting week view, list view etc. needed to be clear too. When users click on buttons they need to know what they are clicking on. "Import Calendar", takes you to the import page, accept or accept all accepts events into the calendar. All of these terms follow real world language so users  know exactly what is happening.

**3. User Control and Freedom**

With a data centric system, users entering invalid data such as wrong file types, invalid event details and more, need to be considered. This is why in our UI, we made sure to explain to users why the system is failing, such as explaining valid file types, telling users to enter valid date times, or that events must have titles if not giving one.

The biggest risk for this would be in our event extraction, as we need to extract valid titles and dates at a minimum. Telling users through the UI of what isn't working is a major component of our UI. User freedom is controlled to the limits of what our system can achieve, whilst allowing them to customise their own calendar to their own needs.

**4. Consistency and Standards**

Users need to know they are on the same website, that's why our website follows a theme the whole way. All web pages follow similar styling, as well as being contextually relevant to the link they follow. We also use language and content relevant to modern calendar systems, as most people would have used, or at least would be familiar with common calendar language.

**5. Error Prevention**

As mentioned in number 3, our UI aims to display good error messages. However we aim to prevent problems from occurring in the first place. Our system doesn't break when users enter invalid event details, and our parsing aims to only extract events in which it is confident in. The only time an error should happen is in a controlled environment caused by a user with invalid file types, event details etc, which shouldn't break the system and should allow users to modify the issue.

**6. Recognition Rather than Recall**

The user flow is relatively simple. Our system doesn't rely on users remembering any information, as the relevant information is displayed wherever they go. They create or edit an event, they can see the fields and information. They import files, they can see the events. They generate smart calendar events and they can see the events created.

**7. Flexibility and Efficiency of Use**

As mentioned in 6, the user flow is simple and as efficient as possible, the only major remark would be allowing users to click on where they want to create an event as being the biggest flexibility and efficiency, as for editing events. This means users don't have to click onto a separate web page, manually enter time details etc.

Another comment would be when images are extracted and the user is in the check events page, they can accept or reject all, meaning users don't waste time manually accepting ore rejecting events based on their needs, but also allowing them to select them one by one if they need to.

**8. Aesthetic and Minimalist Design**

Our UI is designed to be minimalistic with a simple aesthetic design. It is inspired by Google Calendar's Design, being mostly white with line seperations and clear labelling. The whole webapp follows the same aesthetic, with buttons having separate colors to jump out to users so they know where to click, as well as color coding with buttons like accepting being green, rejecting being red, as aspects like that often have an intuitive meaning behind them too.

Events in the check event page needed to be clear and minimalist too, as information with them need to be displayed to the user to allow them to make decisions, as this is the core of the "smartness" of the calendar.

**9. Help Users Recognize, Diagnose, and Recover from Errors**

This has been discussed before, all errors must be communicated and allow the user to recover from them

**10. Help and Documentation**

Our UI is designed to be simple and intuitive, However, some confusion is always inevitable