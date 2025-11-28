# School of Computing
## CA326 Year 3 Project Proposal Form

### SECTION A

| Field | Details |
| :--- | :--- |
| **Project Title** | Smart Schedule Organiser |
| **Staff Member Consulted** | David Sinclair |

**Student Details:**

| Student | Name | ID Number |
| :--- | :--- | :--- |
| **Student 1** | Theo Robin | 23388446 |
| **Student 2** | Amaru Elod Frisancho | 22741819 |

---

### Project Description

#### 1. Description
The proposed project is a Smart Calendar Assistant that can automatically read, interpret, and compile schedules from multiple sources into one unified calendar. Imagine trying to build a schedule or calendar from different sets and sources of overlapping events. Organizing, planning and coordinating everything could take a very long time, and depending on the amount of inputs can become quite complex and hard to manage.

It would take inputs such as imported calendars, files, screenshots, textual information and more and interpret it into a schedule. Instead of manually combining timetables, spreadsheets, and notes, the system will use text recognition and parsing techniques to extract dates, times, and events. It can also then detect overlaps or conflicts and create a clean calendar that can be exported to standard formats such as `.ics` files.

The core input would be files and text. The files could be downloaded/imported calendars, text files, pdf files or more, made possible by the aforementioned method. Aside from using the calendar like a regular one, they can also use a text box that can extract the information to create an event. This is where you can also tell it to include or exclude events from other calendars, or input smart commands that allow you to have complete control over your calendar without spending time manually changing everything. The idea Is you can essentially query it, acting as a fairly rudimentary copilot.

This would be the core of our calendar, however, there is room for more types of inputs such as connected sources, for example Google Calendar or Notion. The possibility of a user being able to take a picture of say a whiteboard or poster showing the week’s schedule and our app being able to make the calendar around that is a future possibility, however, it is very advanced.

This type of project could be used to save hours, if not days of time for users, especially those who need to create schedules and calendars from multiple sources. On top of that, it could be used by schools for creating class schedules in very short amounts of time. As such, The smart calendar assistant would serve individual people and larger organisations.

#### 2. Division of Work
* **Theo:** File ingestion and parsing (Excel, text, notes), conflict detection logic, and back-end calendar data model.
* **Amaru:** Front-end interface (basic web/app view), export to Google Calendar / ICS integration, and testing.

#### 3. Programming Languages
* **Python:** For back-end logic and data extraction.
* **JavaScript (most likely React):** For the user interface.

#### 4. Programming Tools
* **Pandas:** Handling spreadsheets.
* **PDF/Excel parsing libraries:** (e.g., `pdfplumber`, `openpyxl`).
* **Dateparser:** Interpreting dates/times in natural language.
* **Django:** For API/backend services.
* **React:** For front-end.
* **PyTorch:** Can handle screenshots to avoid manually inputting into calendar.
* **Google Calendar API / ics library:** (Possibility in the future) for exporting events.

#### 5. Learning Challenges
* Learning how to parse and interpret semi-structured data (like timetables in PDF or text) using aforementioned tools.
* Understanding recurrence rules and calendar formats.
* Conflict detection and optimization (handling overlapping events).
* Integrating with Google Calendar API.

#### 6. Hardware / Software Problem
* Standard lab PCs. It should work with Windows or Linux.
* **Environment:** Python and Node.js.
* DCU’s Gitlab will be used for collaboration.

#### 7. Special Hardware / Software requirements
* No special hardware required.
* If using it with Google Calendar for example, would need access to Google Calendar API keys for testing.