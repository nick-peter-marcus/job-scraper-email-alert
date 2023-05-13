# webpage-update-alert
Tool for alerting me when the content of a webpage changes.

We'll use Python to fetch the content of webpage and hash this information. After a certain amount of time, we'll fetch again and compare the new with the old hash. If it changed, print a message.

The project's steps might look like this:
1. Use an examplary website to have control over the changes.
2. Extend the alert to not only display <i>that</i> something has changed, but <i>what</i> has changed.
3. Use the extracted info to alert via email.
4. Apply to a real website.
