"""Synthetic SEED data for the 3-class email model (safe / marketing / phishing).

This is only a bootstrap so the pipeline works on modern-looking mail. It is template
based, so it is NOT a measure of real-world accuracy. Replace / add to it with real
labelled mail: put .eml or .txt files in ml/data/modern/{safe,marketing,phishing}/
(see ml/train_email3.py).
"""
import random

BRANDS = {  # name: (official domain, tracking domain used by its marketing mails)
    "Swiggy": ("swiggy.com", "email.swiggy.com"), "Zomato": ("zomato.com", "links.zomato.com"),
    "Amazon": ("amazon.in", "email.amazon.in"), "Flipkart": ("flipkart.com", "click.flipkart.com"),
    "Myntra": ("myntra.com", "email.myntra.com"), "Nykaa": ("nykaa.com", "links.nykaa.com"),
    "MakeMyTrip": ("makemytrip.com", "email.makemytrip.com"), "Netflix": ("netflix.com", "mailer.netflix.com"),
    "Spotify": ("spotify.com", "email.spotify.com"), "Paytm": ("paytm.com", "mail.paytm.com"),
    "HDFC Bank": ("hdfcbank.com", "alerts.hdfcbank.com"), "ICICI Bank": ("icicibank.com", "alerts.icicibank.com"),
    "SBI": ("sbi.co.in", "mail.sbi.co.in"), "LinkedIn": ("linkedin.com", "e.linkedin.com"),
    "Microsoft": ("microsoft.com", "email.microsoft.com"), "Google": ("google.com", "accounts.google.com"),
    "PayPal": ("paypal.com", "e.paypal.com"), "IRCTC": ("irctc.co.in", "mail.irctc.co.in"),
}
GENERIC = {n: d for n, d in [("Notion", "notion.so"), ("Canva", "canva.com"), ("Coursera", "coursera.org"), ("Uber", "uber.com"),
    ("BigBasket", "bigbasket.com"), ("Goibibo", "goibibo.com"), ("Decathlon", "decathlon.in"), ("Udemy", "udemy.com"),
    ("Dropbox", "dropbox.com"), ("Zerodha", "zerodha.com"), ("Meesho", "meesho.com"), ("Lenskart", "lenskart.com"),
    ("PhonePe", "phonepe.com"), ("Airtel", "airtel.in"), ("boAt", "boat-lifestyle.com"), ("Croma", "croma.com"),
    ("Slack", "slack.com"), ("Adobe", "adobe.com"), ("Ola", "olacabs.com"), ("Cult.fit", "cult.fit")]}
ESP = ["list-manage.com", "sendgrid.net", "klclick.com", "mailchimp.com", "clevertap-prod.com"]
BAD_TLD = ["xyz", "top", "click", "buzz", "icu", "live", "shop", "cfd"]
NAMES = ["Rahul", "Priya", "Ankit", "Sneha", "Vikram", "Meera", "Arjun", "Divya", "Karan", "Neha", "Sahil", "Pooja"]
FREE = ["gmail.com", "yahoo.com", "outlook.com", "rediffmail.com"]


def _brand(r):
    if r.random() < 0.5:
        b = r.choice(list(BRANDS)); real, track = BRANDS[b]
    else:
        b = r.choice(list(GENERIC)); real = GENERIC[b]
        track = r.choice(["mail", "email", "click", "links", "e", "news"]) + "." + real
    return b, real, track


def _slug(b):
    return b.lower().replace(" bank", "").replace(" ", "")


def _fake_domain(r, b):
    s = _slug(b)
    return r.choice([f"{s}-secure-kyc.{r.choice(BAD_TLD)}", f"{s}-verify.{r.choice(BAD_TLD)}",
                     f"secure-{s}login.com", f"{s}.account-update.{r.choice(BAD_TLD)}",
                     f"{s}-support-help.com", f"{s}care-alerts.{r.choice(BAD_TLD)}", f"my{s}-rewards.{r.choice(BAD_TLD)}",
                     f"{s}-india-online.net"])


def phishing(r):
    b = r.choice(list(BRANDS)); real = BRANDS[b][0]; fake = _fake_domain(r, b)
    name = r.choice(NAMES)
    kind = r.randrange(10)
    sender = r.choice([f"alerts@{fake}", f"no-reply@{fake}", f"support@{r.choice(FREE)}", f"{_slug(b)}.care@{r.choice(FREE)}", f"security@{fake}"])
    short = r.choice(["http://bit.ly/", "https://tinyurl.com/", "https://cutt.ly/", "https://rb.gy/"]) + "".join(r.choices("abcdefgh123456", k=6))
    url = r.choice([f"http://{fake}/verify", f"https://{fake}/login", short])
    shown = r.choice([real, f"www.{real}", f"https://www.{real}/login", "Click here", "Verify now", "Update KYC"])
    links = [{"href": url, "text": shown}]
    if kind == 0:
        s, t = f"Your {b} account will be blocked today - verify KYC", f"Dear customer, your {b} account will be blocked within 24 hours due to incomplete KYC. Update your PAN and share the OTP sent to your mobile to avoid permanent suspension."
    elif kind == 1:
        s, t = f"{b} password expires in 24 hours", f"Hello {name}, your {b} password expires today. Click the link below to keep your current password and avoid losing access. Failure to verify will lock your account."
    elif kind == 2:
        s, t = "Package could not be delivered", f"We attempted to deliver your parcel but the address was incomplete. Pay a redelivery fee of Rs {r.choice([29, 49, 75, 99])} within 12 hours or the package will be returned. Confirm your card details here."
    elif kind == 3:
        s, t = "Income tax refund pending", f"Dear taxpayer, a refund of Rs {r.randint(8, 48)},{r.randint(100, 999)} is approved for your PAN. Submit your bank account and debit card details to receive the refund immediately."
    elif kind == 4:
        s, t = f"Unusual sign-in to your {b} account", f"We detected a suspicious login from a new device. If this was not you, confirm your identity and enter your password at the secure link below, otherwise your account will be restricted."
    elif kind == 5:
        s, t = f"Payment failed - {b} subscription suspended", f"Your last payment could not be processed and your membership is on hold. Update your payment method now to avoid cancellation. Dear valued customer, act immediately."
    elif kind == 6:
        s, t = f"Congratulations! You have won a {b} reward", f"Dear user, you have been selected for a Rs {r.choice([5000, 10000, 50000])} reward. Claim your gift today only. A small processing fee of Rs {r.choice([99, 199, 499])} is required to release it."
    elif kind == 7:
        s, t = f"Invoice #{r.randint(1000, 99999)} attached", f"Please find the attached invoice and open the file to review payment details. Download the document and enable content to view it. Urgent: payment is overdue."
        links = [{"href": url, "text": "Invoice.html"}]
    elif kind == 8:
        fee = r.choice(["registration fee", "security amount", "training deposit"])
        s, t = "Job offer - registration fee", (f"Dear candidate, you are shortlisted for a work-from-home job at {b}. Earn Rs 30,000 per week. "
            f"Deposit a refundable {fee} of Rs {r.choice([499, 999, 1500])} to confirm your seat and contact us on WhatsApp +91 9{r.randint(100000000, 999999999)}.")
        links = []
    else:
        s, t = "Quick favour - urgent", f"Hi {name}, I'm in a meeting and need you to buy gift cards for a client today. Reply immediately with the codes. I will reimburse you. Do not call, only email."
        sender = f"ceo.office{r.randint(1, 99)}@{r.choice(FREE)}"; links = []
    return dict(sender=sender, subject=s, body=t, links=links, label="phishing")


def marketing(r):
    b, real, track = _brand(r)
    kind = r.randrange(9); name = r.choice(NAMES)
    sender = r.choice([f"offers@{real}", f"no-reply@{real}", f"newsletter@{track}", f"hello@{real}", f"deals@{track}"])
    tr = r.choice([track, r.choice(ESP), real])
    links = [{"href": f"https://{tr}/c/{r.randint(1000, 99999)}", "text": r.choice(["Shop now", "Order now", "View offers", "Explore"])} for _ in range(r.randint(2, 6))]
    links.append({"href": f"https://{tr}/unsubscribe", "text": "Unsubscribe"})
    foot = r.choice(["You are receiving this email because you subscribed. Unsubscribe | Manage preferences", "View this email in your browser. To stop receiving these emails, unsubscribe here.", "Unsubscribe anytime. T&C apply."])
    off = r.choice([20, 30, 40, 50, 60, 70])
    if kind == 0:
        s, t = f"{off}% off on your next order!", f"Hi {name}, get {off}% off with code SAVE{off}. Order now before the offer ends Sunday. Shop your favourites on {b}."
    elif kind == 1:
        s, t = f"{b} Festival Sale is live", f"The biggest sale of the year has started. Up to {off}% off on electronics, fashion and home. Limited time offer, shop now and save big!"
    elif kind == 2:
        s, t = f"{name}, you left something in your cart", f"Your cart is waiting. Complete your purchase today and get free delivery. Bestsellers are selling fast, don't miss out!"
    elif kind == 3:
        s, t = f"New arrivals just for you", f"Hi {name}, check out our latest collection picked for you. New arrivals, trending styles and exclusive deals. Shop now."
    elif kind == 4:
        s, t = f"Your weekly {b} digest", f"Here are this week's top stories, tips and product updates from {b}. Read more on our blog and discover new features."
    elif kind == 5:
        s, t = f"Introducing our new app", f"We have launched a redesigned app with faster checkout and cashback offers. Download the app from the Play Store or App Store and get Rs {r.choice([50, 100, 200])} cashback on your first order."
    elif kind == 7:
        s, t = f"What's new at {b} this month", f"We shipped new features, templates and faster performance. Read the full release notes on our blog and try them free for 30 days. Upgrade to Pro for more."
    elif kind == 8:
        n = r.choice([1999, 2499, 2999, 3499])
        s, t = f"Fares starting at Rs {n} this season", f"Grab the lowest prices, limited seats. Book now and save up to Rs 1,500 with code GO{n}. Pick up where you left off."
    else:
        s, t = f"Last few hours: flat {off}% off", f"Hurry, today only! Flat {off}% off sitewide plus an extra bank offer. Use code FEST{off}. Terms and conditions apply."
    return dict(sender=sender, subject=s, body=t + "\n\n" + foot, links=links, label="marketing")


def safe(r):
    name, name2 = r.sample(NAMES, 2)
    kind = r.randrange(9)
    b, real, track = _brand(r)
    sender = f"{name2.lower()}@{r.choice(['company.in', 'acme.com', 'college.edu', 'gmail.com', 'outlook.com'])}"
    links = []
    if kind == 0:
        s, t = "Standup moved to 11am", f"Hi {name}, can we move tomorrow's standup to 11am? I have the design review at 10. Thanks, {name2}"
    elif kind == 1:
        s, t = "Notes from today's meeting", f"Hey {name}, sharing the notes from today. Action items: finalize the report by Friday, and let me know if you need help with the data. Regards, {name2}"
    elif kind == 2:
        otp = r.randint(100000, 999999)
        s, t = f"{b}: your one-time password", f"Your OTP for logging in to {b} is {otp}. Do not share it with anyone, including {b} staff. Valid for 10 minutes. If you did not request this, please ignore this email."
        sender = f"alerts@{real}"
    elif kind == 3:
        s, t = f"Your order #{r.randint(10000, 999999)} has shipped", f"Thanks for your order. Your package has been dispatched and will arrive on Thursday. You can track your order in your account. Invoice is attached."
        sender = f"orders@{real}"; links = [{"href": f"https://www.{real}/orders", "text": "Track your order"}]
    elif kind == 4:
        s, t = f"Rs {r.randint(100, 9000)} debited from your account", f"Dear customer, Rs {r.randint(100, 9000)} was debited from your account ending {r.randint(1000, 9999)} on UPI. If this was not you, call the number on the back of your card. Never share your PIN or OTP."
        sender = f"alerts@{real}"
    elif kind == 5:
        s, t = "[org/repo] New commit pushed to main", f"{name2} pushed 2 commits to main. View changes on GitHub. You are receiving this because you are watching this repository."
        sender = "notifications@github.com"; links = [{"href": "https://github.com/org/repo/commit/abc123", "text": "View changes"}]
    elif kind == 6:
        s, t = "Invitation: project review @ Tue 3pm", f"{name2} has invited you to a meeting. Join with Google Meet. Agenda: roadmap review and budget. Let me know if you cannot make it."
        sender = "calendar-notification@google.com"; links = [{"href": "https://meet.google.com/abc-defg-hij", "text": "Join with Google Meet"}]
    elif kind == 7:
        s, t = "Assignment submission deadline", f"Dear students, please submit your assignment on the portal by Friday 5 pm. Late submissions will lose marks. Contact me if you have questions. Regards, Prof. {name2}"
        sender = f"prof.{name2.lower()}@college.edu"
    else:
        s, t = "Dinner on Sunday?", f"Hi {name}, are you free on Sunday? Mom is making biryani. Let me know and bring the photos from the trip. See you!"
        sender = f"{name2.lower()}@gmail.com"
    return dict(sender=sender, subject=s, body=t, links=links, label="safe")


def generate(n_per_class=500, seed=7):
    r = random.Random(seed)
    out = []
    for _ in range(n_per_class):
        out += [phishing(r), marketing(r), safe(r)]
    return out
