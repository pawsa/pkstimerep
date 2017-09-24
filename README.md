PKS Time report
===============

Cloud-enabled time report. It enables:
- User:
-- registering arrival, departure, break times
-- registering vacation, sick and parental leaves.
-- locking weeks.
- Admin:
-- adding and disabling users, setting overtime limits.
-- unlocking weeks.
- User+viewer+admin:
-- browsing reports, overtime status.

Client
======

Boostrap and angular based, with three sides separated so that regular
users do not need to load page administration code etc
.
The operation modes:

1. Select user and mode, if available.

2. For the regular user: open the oldest still editable weekly report;
   display overtime status.

2.1. available operations - set current arrival or departer if dates
     permit, set explicitly date, break, leave times, or day type;
     lock week.

3. For the viewer: permit selecting other user, display current ovetime
   status and navigable monthly status.

4. For the admin: display menu with selection of: a) user management
b) unlocking system. c) bank holiday edition,

4.1. user managements permits: creating user, listing them, updating
name or overtime limits and weekly amounts, disabling and enabling
users.

4.2. unlocking provides ability to select an user, and clear
aggregates locked weeks until some date. (confirmable)

4.1. bank holiday edition provides ability to: list red days per year
(date, name), b) remove b) add c) edit date d) create next year based
on previous.


Server
======

The application is protected by an Identity Aware Proxy. The app has
internal access management, relying on the user status set in in a
expirable token. When token expires or is not available, IAP identity
is checked to reassert rights.

The following endpoints are provided. Endpoints marked with * will be
not provided by MVP. Appropriate access checks are executed.

POST /user - adds a new user.
GET /user - list users, basic metadata - not paged.
*GET /user/userid - list specific user to save bandwidth if needed.
PATCH /user/userid/meta - alter the user data
PATCH /user/userid/active user activation and deactivation.


GET /user/userid/day?start=YYYY-MM-DD&end=YYYY-MM-DD
 - returns day statuses, entry, leave and break times times. If range unspecified,
   returns data for the most recent unlocked week.

PATCH /user/userid/day/YYY-MM-DD - sets day properties
* DELETE /user/userid/day/YYY-MM-DD - clear any prior data if present

POST /user/userid/report with {year: YYYY, week: WEEKNO} - locks the
 week provided all the data is in place.

GET /user/userid/report - get the overtime status and the last locked
 week (returned alos by /user/userid?)

DELETE /user/userid/report/YYYY-WW - delete given weekly report

POST /holiday { date: YYYY-MM-DD, name: NAME} Add a holiday
GET /holiday?year=YYYY - list the holidays for given year (date, name, id)
PATCH /holiday/id - change the name or date for given holiday
*DELETE /holiday/id - delete given holiday
