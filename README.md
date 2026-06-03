

# HindenBurg-Research-Alert
The main script is Hindenburg_run.py. Hindenburg_proxy.py is cloudfare workaround and probably not a very good one at that

Sends an immediate text alert when HindenBurg publishes a new report.


https://hindenburgresearch.com/ is a famous short selling group that researches and publishes reports on stocks they're shorting. They have a financial incentive in seeing these companies fail but they have built a reputation on Wall St for being largely correct in their reports.

So when they call out a company that is cooking the books or in some way being dishonest, they usually drop a stock by 25-30% in a single day.
If someone could be immediately notified of these reports, they could profit off that move. 

Create a free python anywhere account or a small linux container on aws

Bash console -----

pip install requests beautifulsoup4 twilio


You will also need to set up a Twilio account for the outbound phone text
Instructions for the proxy version are commented in the main file


