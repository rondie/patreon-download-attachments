# patreon-download-attachments
Python script to download attachments from patreon

I needed a way to automatically download files from creators I support, as they keep files up for a month or so and are then deleted. This script fills that need for me.

Because of the way patreon MFA works, after running the script the first time, you need to click the link in the email you've received (script output tells you as well), and then you should be ok to run it again. The cookiefile keeps the session, not sure how often it should be run to keep it alive, or when/if it does expire.
