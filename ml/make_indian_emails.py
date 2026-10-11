"""Generate a synthetic, India-focused email dataset (phishing vs legitimate).

Output columns: text,label,language,type,source   (source is always 'synthetic')
Run:  python3 make_indian_emails.py            -> indian_emails.csv
Edit the templates to add your own wording, then re-run.
NOTE: synthetic data. Use it for TRAINING only; test on real emails you collect.
"""
import csv
import random

random.seed(7)

NAMES = ["Rahul", "Priya", "Amit", "Sneha", "Rohan", "Pooja", "Vikram", "Anjali", "Karan", "Neha", "Suresh", "Divya", "Manoj", "Kavita"]
BANKS = {  # name -> (fake slug, real domain)
    "SBI": ("sbi", "sbi.co.in"), "HDFC Bank": ("hdfc", "hdfcbank.com"), "ICICI Bank": ("icici", "icicibank.com"),
    "Axis Bank": ("axis", "axisbank.com"), "Punjab National Bank": ("pnb", "pnbindia.in"),
    "Bank of Baroda": ("bob", "bankofbaroda.in"), "Kotak Mahindra Bank": ("kotak", "kotak.com"),
}
FAKE_TLD = ["xyz", "top", "click", "icu", "live", "shop", "buzz", "cfd"]
FAKE_WORD = ["kyc-update", "verify-now", "secure-login", "account-verify", "update-details", "reactivate", "claim-reward"]
SHOPS = ["Amazon", "Flipkart", "Myntra", "Meesho", "Swiggy", "Zomato", "Nykaa"]
COLLEGES = ["the Department of Computer Science", "the Examination Cell", "the Training and Placement Cell", "the Library", "the Hostel Office"]
MERCH = ["Zomato", "Swiggy", "Amazon", "IRCTC", "BigBasket", "Uber", "Jio Recharge", "Airtel Postpaid"]
COURIERS = ["India Post", "Blue Dart", "DTDC", "Delhivery"]


# ---- e-commerce / platform footers and fields (hard negatives AND look-alike phishing) ----
ITEMS = ["Asymmetric Bikini Set", "Cotton Kurta Set", "Wireless Earbuds", "Running Shoes", "Floral Midi Dress", "Phone Case", "Backpack 30L", "Steel Water Bottle"]
BRANDS = ["Savana by Urbanic", "Urbanic", "Nike", "boAt", "Puma", "Biba", "Zudio", "Max Fashion"]
VENDORS = ["Google", "GitHub", "Kaggle", "Notion", "Slack", "Zoom", "Microsoft", "LinkedIn"]
PRODUCTS = ["Gemini", "Cloud Run", "Colab", "Sheets API", "Copilot", "Teams"]
DEVICES = ["Chrome on Mac", "an Android phone", "Windows PC", "iPhone"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONS = ["Sep", "Oct", "Nov"]
FOOT_E = [
    "Download the {shop} mobile app for faster checkout and exclusive offers. Manage your account, track orders and returns in one place. Visit {site} for help. Follow us on Instagram and Facebook. {shop} Pvt Ltd, 4th Floor, Tower B, Bengaluru 560001. You are receiving this email because you placed an order on our site. Unsubscribe.",
    "Need help? Visit our Help Centre at {site}/help or reply to this email. Log in to your account to view your orders, addresses and saved payment methods. Get the app on Google Play and the App Store. Terms of Use | Privacy Policy | Unsubscribe",
    "Shop the new arrivals on {site}. Install our mobile app and get 10% off your next order. Your account, your orders, your rewards - all in the app. This is an automated email, please do not reply. {shop} India, Mumbai 400013.",
]
FOOT_S = [
    "You received this email to let you know about important changes to your {vendor} account and services. {vendor} LLC, 1600 Amphitheatre Parkway, Mountain View, CA 94043. Unsubscribe.",
    "You are receiving this because you have an account on {site}. Manage your notification settings on our site or in the mobile app. Privacy Policy | Unsubscribe.",
]


def _extend(c):
    c["site"] = f"www.{c['shop'].lower()}.com"
    c["item"], c["brand"] = random.choice(ITEMS), random.choice(BRANDS)
    c["vendor"], c["product"] = random.choice(VENDORS), random.choice(PRODUCTS)
    c["ver"] = f"{random.randint(1, 4)}.{random.randint(0, 9)}"
    c["ver2"] = f"{random.randint(1, 4)}.{random.randint(0, 9)}"
    c["device"] = random.choice(DEVICES)
    c["day"], c["mon"], c["d"] = random.choice(DAYS), random.choice(MONS), random.randint(1, 28)
    c["longorder"] = "S" + "".join(random.choices("0123456789", k=random.randint(16, 20)))
    c["foot_e"] = random.choice(FOOT_E).format(**c)
    c["app"] = random.choice(["Kaggle", "Canva", "Spotify", "Notion"])
    c["foot_s"] = random.choice(FOOT_S).format(**c)
    return c


def ctx():
    b = random.choice(list(BANKS))
    slug, real = BANKS[b]
    fake = f"http://{slug}-{random.choice(FAKE_WORD)}.{random.choice(FAKE_TLD)}"
    if random.random() < 0.3:
        fake = random.choice(["https://bit.ly/", "https://cutt.ly/", "https://tinyurl.com/"]) + "".join(random.choices("abcdefghjkmnpqrstuvwxyz23456789", k=6))
    amt = random.choice([499, 999, 1500, 2350, 4999, 5000, 7800, 12000, 15490, 25000, 49999])
    return _extend(dict(
        name=random.choice(NAMES), bank=b, fake=fake, real=real, slug=slug,
        amt=f"{amt:,}", big=random.choice(["10,00,000", "25,00,000", "5,00,000", "50,00,000"]),
        fee=random.choice([299, 499, 750, 999, 1500, 2100]),
        hrs=random.choice([2, 6, 12, 24, 48]), last4=f"{random.randint(1000, 9999)}",
        phone=f"{random.choice('6789')}{random.randint(100000000, 999999999)}",
        ref=f"{random.randint(100000, 999999)}", date=f"{random.randint(1, 28):02d}-{random.randint(1, 12):02d}-2026",
        shop=random.choice(SHOPS), merch=random.choice(MERCH), courier=random.choice(COURIERS),
        dept=random.choice(COLLEGES), otp=f"{random.randint(100000, 999999)}", order=f"{random.randint(100, 999)}-{random.randint(1000000, 9999999)}",
    ))


# ---------------- PHISHING ----------------
P = {}
P[("kyc", "en")] = [
    "Subject: Urgent: {bank} KYC expired\n\nDear Customer, your {bank} account will be blocked within {hrs} hours because your KYC is not updated. Update now: {fake}\nFailure to comply will result in permanent suspension.\n{bank} Customer Care",
    "Subject: Your {bank} account has been suspended\n\nDear {name}, we noticed suspicious activity. Your account is temporarily restricted. Verify your PAN and Aadhaar details immediately at {fake} to restore access. Do not ignore this message.",
    "Subject: Final reminder - complete KYC\n\nHello {name}, as per RBI guidelines you must complete re-KYC today or your {bank} account will be closed. Click here and enter your card number, CVV and OTP: {fake}",
]
P[("kyc", "hinglish")] = [
    "Subject: {bank} KYC update zaruri hai\n\nPriya ji, aapka {bank} account {hrs} ghante mein band ho jayega. Abhi KYC update karein is link par: {fake} warna account block ho jayega.",
    "Subject: Account block hone wala hai\n\nDear {name}, aapke {bank} account me KYC pending hai. Aaj hi PAN aur Aadhaar verify karein: {fake}. Der na karein.",
]
P[("kyc", "hi")] = [
    "विषय: आपका {bank} खाता बंद होने वाला है\n\nप्रिय ग्राहक, आपकी KYC अधूरी है। {hrs} घंटे में अपडेट नहीं किया तो खाता बंद कर दिया जाएगा। अभी इस लिंक पर क्लिक करें: {fake}",
]
P[("kyc", "mr")] = [
    "विषय: तुमचे {bank} खाते बंद होणार आहे\n\nप्रिय ग्राहक, तुमचे KYC अपडेट केलेले नाही. {hrs} तासांत अपडेट न केल्यास खाते ब्लॉक होईल. आत्ताच लिंकवर क्लिक करा: {fake}",
]
P[("itr", "en")] = [
    "Subject: Income Tax Refund approved\n\nDear Taxpayer, your refund of Rs {amt} has been approved by the Income Tax Department. To credit it, verify your bank details at {fake} within {hrs} hours. Refund will be cancelled otherwise.",
    "Subject: Pending tax refund Rs {amt}\n\nHello {name}, a refund is pending against your PAN. Click {fake} and submit your debit card number and PIN to receive the amount.",
]
P[("lottery", "en")] = [
    "Subject: Congratulations! You have won Rs {big}\n\nDear {name}, you have been selected as the lucky winner of the KBC Lottery 2026. Claim your prize of Rs {big} by paying a processing fee of Rs {fee}. Contact WhatsApp {phone} now. Offer valid for {hrs} hours only.",
    "Subject: You won an iPhone 16 Pro!\n\nCongratulations {name}! You are today's lucky customer. Pay only Rs {fee} delivery charges and claim your free iPhone: {fake}. Hurry, limited stock.",
]
P[("lottery", "hinglish")] = [
    "Subject: Aap jeet gaye Rs {big}!\n\nBadhai ho {name} ji! Aap KBC lucky draw ke winner hain. Prize lene ke liye Rs {fee} processing fee bhejein aur is number par WhatsApp karein: {phone}. Sirf {hrs} ghante bache hain.",
]
P[("lottery", "hi")] = [
    "विषय: बधाई हो! आपने Rs {big} जीते हैं\n\nप्रिय {name}, आप KBC लकी ड्रॉ के विजेता हैं। इनाम पाने के लिए Rs {fee} शुल्क जमा करें और {phone} पर व्हाट्सएप करें।",
]
P[("jobfee", "en")] = [
    "Subject: Work from home - earn Rs 5000 daily\n\nDear {name}, we are hiring part-time data entry staff. No experience needed. Earn Rs 5000 per day from home. Pay a one-time registration fee of Rs {fee} to confirm your seat. WhatsApp {phone}.",
    "Subject: Job offer letter - Infosys HR\n\nCongratulations, you are selected for a position at our company. To receive the appointment letter please pay a security deposit of Rs {fee} to the account given below. Confirm within {hrs} hours.",
]
P[("jobfee", "hinglish")] = [
    "Subject: Ghar baithe kamao 5000 rupaye daily\n\nHello {name}, hamare yahan part time job available hai. Registration fee sirf {fee} Rs. Abhi WhatsApp karein {phone}. Seats limited hain.",
]
P[("jobfee", "mr")] = [
    "विषय: घरबसल्या दिवसाला 5000 रुपये कमवा\n\nनमस्कार {name}, आमच्याकडे पार्ट टाइम नोकरी उपलब्ध आहे. नोंदणी शुल्क फक्त Rs {fee}. आत्ताच {phone} वर व्हॉट्सअ‍ॅप करा.",
]
P[("govt", "en")] = [
    "Subject: PM Yojana - free Rs {amt} for every citizen\n\nThe Government of India is giving Rs {amt} to all citizens under the new PM scheme. Register now at {fake} with your Aadhaar and bank account number. Share this with 10 friends to get the benefit.",
    "Subject: Free laptop scheme 2026\n\nDear student, apply for the government free laptop scheme. Pay Rs {fee} registration and submit your Aadhaar here: {fake}. Last date today.",
]
P[("courier", "en")] = [
    "Subject: {courier}: your parcel is on hold\n\nDear {name}, your parcel could not be delivered due to an incomplete address. Pay a redelivery fee of Rs {fee} at {fake} within {hrs} hours or it will be returned.",
    "Subject: Customs duty payment required\n\nYour international package is held at customs. Pay Rs {fee} duty at {fake} to release it. Tracking ID {ref}.",
]
P[("electric", "en")] = [
    "Subject: Electricity connection will be disconnected tonight\n\nDear Consumer, your power supply will be cut at 9:30 PM today because last month's bill is unpaid. Contact our officer immediately on {phone} and pay by the link {fake}.",
]
P[("electric", "hinglish")] = [
    "Subject: Bijli connection aaj raat kat jayega\n\nPriya ji, aapka pichla bill pending hai. Aaj raat 9:30 baje connection kat jayega. Turant is number par call karein {phone} aur {fake} par payment karein.",
]
P[("upi", "en")] = [
    "Subject: You have received a refund of Rs {amt}\n\nHello {name}, a payment refund of Rs {amt} is waiting. Open {fake} and enter your UPI PIN to accept the money.",
    "Subject: Cashback Rs {amt} credited - claim now\n\nCongratulations! Cashback of Rs {amt} is ready. Scan the QR code or enter your UPI PIN at {fake} to receive it. Expires in {hrs} hours.",
]
P[("upi", "hinglish")] = [
    "Subject: Cashback aapka intezaar kar raha hai\n\n{name} ji, aapke liye Rs {amt} ka cashback hai. Paise lene ke liye is link par UPI PIN dalein: {fake}. {hrs} ghante me expire.",
]
P[("sim", "en")] = [
    "Subject: Your SIM will be deactivated\n\nDear customer, your mobile number will be blocked in {hrs} hours as per TRAI directive. Verify your Aadhaar at {fake} or call {phone} to avoid disconnection.",
]
P[("reward", "en")] = [
    "Subject: Your {bank} reward points expire today\n\nDear {name}, reward points worth Rs {amt} will expire tonight. Redeem them now by installing our app: {fake}/rewards.apk. Offer valid for today only.",
]
P[("account", "en")] = [
    "Subject: {shop} account suspended\n\nWe could not verify your payment information so your {shop} account has been put on hold. Update your card details within {hrs} hours at {fake} to avoid permanent closure.",
    "Subject: Security alert: unusual sign-in\n\nHi {name}, someone tried to sign in to your account. Confirm it was you by entering your password and OTP here: {fake}",
]

# ---------------- LEGITIMATE ----------------
L = {}
L[("debit", "en")] = [
    "Subject: Transaction alert\n\nDear {name}, Rs {amt}.00 has been debited from your A/c XX{last4} on {date} via UPI to {merch}. Ref no {ref}. Available balance Rs 18,420.55. If you did not make this transaction, call the number on the back of your card or visit {real}. - {bank}",
    "Subject: {bank}: Debit Alert\n\nRs {amt} debited from account ending {last4} on {date}. Merchant: {merch}. If this was not you, please report it through the official {bank} app or visit your nearest branch.",
]
L[("credit", "en")] = [
    "Subject: Credit alert\n\nDear {name}, your account XX{last4} has been credited with Rs {amt}.00 on {date}. Ref {ref}. Thank you for banking with {bank}.",
]
L[("otp", "en")] = [
    "Subject: Your one time password\n\n{otp} is your OTP for logging in to {bank} NetBanking. It is valid for 10 minutes. Do not share this OTP with anyone, including bank staff.",
    "Subject: OTP for transaction\n\nUse OTP {otp} to authorise a payment of Rs {amt} to {merch}. Valid for 5 minutes. Never share your OTP. If you did not request this, ignore this email.",
]
L[("awareness", "en")] = [
    "Subject: Stay safe from fraud - a message from {bank}\n\nDear {name}, {bank} never asks for your OTP, PIN, CVV or password by email, phone or SMS. Do not click on links in unknown messages asking you to update KYC. For any KYC update visit your branch or log in at {real}. Report suspicious messages to the bank's official helpline.",
]
L[("order", "en")] = [
    "Subject: Your {shop} order has been shipped\n\nHi {name}, good news! Your order #{order} has shipped and will arrive by Thursday. You can track your package in the {shop} app under Your Orders. Thanks for shopping with us.",
    "Subject: Delivered: your {shop} order\n\nYour order #{order} was delivered today. We hope you enjoy it. Not satisfied? You can return items within 10 days from the Orders page. Rate your purchase in the app.",
]
L[("order", "hinglish")] = [
    "Subject: Aapka {shop} order ship ho gaya hai\n\nHi {name}, aapka order #{order} ship ho gaya hai aur kal tak deliver hoga. Tracking ke liye app me Your Orders dekhein. Dhanyavaad!",
]
L[("college", "en")] = [
    "Subject: Semester exam timetable\n\nDear students, the end-semester examination timetable has been uploaded on the college portal. Please check the notice board of {dept}. Hall tickets will be issued from Monday. Contact the department office for queries.",
    "Subject: Placement drive next week\n\nDear {name}, {dept} is organising a campus placement drive on {date}. Eligible students should register on the portal before Friday and carry their resume and ID card.",
]
L[("college", "hi")] = [
    "विषय: परीक्षा समय सारणी\n\nप्रिय विद्यार्थियों, सेमेस्टर परीक्षा की समय सारणी कॉलेज पोर्टल पर अपलोड कर दी गई है। कृपया {dept} के नोटिस बोर्ड पर देखें। किसी भी प्रश्न के लिए विभाग कार्यालय से संपर्क करें।",
]
L[("college", "mr")] = [
    "विषय: परीक्षेचे वेळापत्रक\n\nप्रिय विद्यार्थ्यांनो, सत्र परीक्षेचे वेळापत्रक महाविद्यालयाच्या पोर्टलवर उपलब्ध आहे. कृपया सूचना फलक पहा. अधिक माहितीसाठी विभाग कार्यालयाशी संपर्क साधा.",
]
L[("marketing", "en")] = [
    "Subject: CAT 2027 - previous year cutoffs\n\nHi {name}, category-wise CAT cut-offs for IIMs are here. IIMs also consider your sectional performance during shortlisting, so keep your preparation balanced. Achieve 99 percentile and get 50% refund on our course. Any queries? Please WhatsApp to {phone}.\n\nYou are receiving these emails because you subscribed to our mailing list for important updates. Unsubscribe anytime.",
    "Subject: Festive sale starts tomorrow\n\nHi {name}, our biggest sale of the year starts tomorrow. Enjoy up to 60% off and free delivery on orders above Rs 499. Offer valid till Sunday. Questions? Call our support team on {phone}.\n\nYou are receiving this because you subscribed to {shop} offers. Unsubscribe.",
    "Subject: This week on our blog\n\nFive tips for learning Python, a new tutorial on data analysis and our upcoming free webinar. Read more on our website. To stop receiving these emails, click unsubscribe below.",
]
L[("marketing", "hinglish")] = [
    "Subject: Diwali sale shuru!\n\n{name} ji, hamari Diwali sale kal se shuru ho rahi hai. 50% tak ki chhoot aur free delivery. Kisi bhi sawal ke liye support se {phone} par sampark karein. Unsubscribe karne ke liye neeche click karein.",
]
L[("invoice", "en")] = [
    "Subject: Invoice for September\n\nHi {name}, please find attached the invoice for September, amount Rs {amt}. Payment is due by 30 October via bank transfer to the account details on the invoice. Let me know if you have any questions.",
]
L[("work", "en")] = [
    "Subject: Notes from yesterday's meeting\n\nHi team, attaching the notes from yesterday. Can we meet Thursday at 3 to go over the budget and the next sprint? Please add any agenda items before then.",
    "Subject: Project update\n\nHi {name}, the draft report is ready for review. I have shared the document with edit access. Please add comments by Friday and we will finalise on Monday.",
]
L[("bill", "en")] = [
    "Subject: Your electricity bill for October\n\nDear Consumer, your bill of Rs {amt} for the billing period ending {date} is now available. Pay online by the due date through the official MSEDCL website or app. Consumer no. {ref}.",
]
L[("travel", "en")] = [
    "Subject: Booking confirmed - PNR {ref}\n\nDear {name}, your train ticket is confirmed. PNR {ref}, departure {date}. Carry a valid photo ID during travel. Wishing you a pleasant journey. - IRCTC",
]
L[("jobapp", "en")] = [
    "Subject: We received your application\n\nDear {name}, thank you for applying. Our recruitment team is reviewing your profile and will contact you if shortlisted. You can track your application status on the careers portal. There is no fee at any stage of our hiring process.",
]
L[("receipt", "en")] = [
    "Subject: Receipt for your subscription\n\nHi {name}, thanks for your payment of Rs {amt}. Your subscription renews on {date}. You can manage or cancel it anytime from your account settings.",
]
L[("statement", "en")] = [
    "Subject: Your {bank} e-statement is ready\n\nDear {name}, your account statement for the month is ready. Log in to NetBanking at {real} or the {bank} mobile app to view or download it. This is an automated message, please do not reply.",
]
L[("webinar", "en")] = [
    "Subject: Free webinar on Friday\n\nHi {name}, join us for a free webinar on career paths in data science this Friday at 6 PM. Register on our website. A recording will be shared with all registrants.",
]


# --- extra genuine non-English templates so language does not predict the label ---
L[("debit", "hinglish")] = [
    "Subject: Transaction alert\n\n{name} ji, aapke A/c XX{last4} se Rs {amt} {date} ko UPI se {merch} ko debit hue hain. Ref {ref}. Agar yeh transaction aapne nahi kiya to apne bank ki official app ya branch se sampark karein. - {bank}",
]
L[("otp", "hinglish")] = [
    "Subject: Aapka OTP\n\n{otp} aapka {bank} NetBanking login OTP hai. 10 minute tak valid hai. Yeh OTP kisi ke saath share na karein, bank staff ke saath bhi nahi.",
]
L[("bill", "hinglish")] = [
    "Subject: Aapka bijli bill taiyar hai\n\n{name} ji, {date} tak ka bijli bill Rs {amt} ka aa gaya hai. Official website ya app se due date se pehle payment karein. Consumer no {ref}.",
]
L[("awareness", "hinglish")] = [
    "Subject: Fraud se bachein - {bank} ki salah\n\n{bank} kabhi bhi email ya SMS par OTP, PIN ya password nahi maangta. KYC update ke liye kisi unknown link par click na karein, apni branch jayein ya {real} par login karein.",
]
L[("debit", "hi")] = [
    "विषय: लेन-देन अलर्ट\n\nप्रिय {name}, आपके खाते XX{last4} से Rs {amt} {date} को UPI द्वारा {merch} को डेबिट किए गए हैं। संदर्भ संख्या {ref}। यदि यह लेन-देन आपने नहीं किया है तो कृपया बैंक की आधिकारिक ऐप या शाखा से संपर्क करें। - {bank}",
]
L[("otp", "hi")] = [
    "विषय: आपका OTP\n\n{otp} आपका {bank} नेटबैंकिंग लॉगिन OTP है। यह 10 मिनट के लिए मान्य है। इसे किसी के साथ साझा न करें।",
]
L[("order", "hi")] = [
    "विषय: आपका {shop} ऑर्डर भेज दिया गया है\n\nनमस्ते {name}, आपका ऑर्डर #{order} भेज दिया गया है और गुरुवार तक पहुँच जाएगा। ट्रैकिंग के लिए ऐप में आपके ऑर्डर देखें। धन्यवाद!",
]
L[("debit", "mr")] = [
    "विषय: व्यवहार सूचना\n\nप्रिय {name}, तुमच्या खाते XX{last4} मधून Rs {amt} {date} रोजी UPI द्वारे {merch} ला डेबिट झाले आहेत. संदर्भ क्रमांक {ref}. हा व्यवहार तुम्ही केला नसल्यास बँकेच्या अधिकृत अ‍ॅपद्वारे किंवा शाखेत संपर्क करा. - {bank}",
]
L[("order", "mr")] = [
    "विषय: तुमची {shop} ऑर्डर पाठवली आहे\n\nनमस्कार {name}, तुमची ऑर्डर #{order} पाठवली आहे आणि गुरुवारपर्यंत पोहोचेल. ट्रॅकिंगसाठी अ‍ॅपमध्ये तुमच्या ऑर्डर पहा. धन्यवाद!",
]
L[("otp", "mr")] = [
    "विषय: तुमचा OTP\n\n{otp} हा तुमचा {bank} नेटबँकिंग लॉगिन OTP आहे. तो 10 मिनिटांसाठी वैध आहे. कृपया तो कोणाशीही शेअर करू नका.",
]


def build(table, label, per_family):
    rows = []
    for (kind, lang), temps in table.items():
        for _ in range(per_family):
            t = random.choice(temps).format(**ctx())
            rows.append({"text": t, "label": label, "language": lang, "type": kind, "source": "synthetic"})
    return rows


rows = []
for _ in range(1):
    pass
# more draws for English families, fewer for the small non-English ones
rows += build({k: v for k, v in P.items() if k[1] == "en"}, "phishing", 14)
rows += build({k: v for k, v in P.items() if k[1] != "en"}, "phishing", 14)
rows += build({k: v for k, v in L.items() if k[1] == "en"}, "legitimate", 11)
rows += build({k: v for k, v in L.items() if k[1] != "en"}, "legitimate", 10)

# ---- hard negatives: genuine e-commerce / platform emails WITH app, account, site and footer wording ----
L2 = {}
L2[("ecom_ship", "en")] = [
    "Subject: {shop}: Your order has been shipped!\n\n{item}\n1 item from {brand}\nShipped {day}, {mon} {d}\nOrder number {longorder}\nView order\n\n{foot_e}",
    "Subject: Your {shop} order is out for delivery\n\nHi {name}, your order of {item} is out for delivery today. Order number {longorder}. Track your order in the mobile app or on {site}.\n\n{foot_e}",
]
L2[("ecom_deliv", "en")] = [
    "Subject: Delivered: {item}\n\n{item}\n1 item from {brand}\nDelivered {day}, {mon} {d}\nOrder number {longorder}\nView order\nRate your purchase or start a return from your account.\n\n{foot_e}",
]
L2[("ecom_refund", "en")] = [
    "Subject: Your refund of Rs {amt} has been processed\n\nHi {name}, we have processed your refund of Rs {amt} for order {longorder}. It will reflect in your original payment method in 5-7 business days. No action is needed from you. Track the status of your refund in your account on {site}.\n\n{foot_e}",
]
L2[("ecom_confirm", "en")] = [
    "Subject: Order confirmed - {shop}\n\nThanks for your order, {name}! We have received your payment of Rs {amt}. Order number {longorder}. You can manage your order, change your delivery address or cancel it from your account until it ships.\n\n{foot_e}",
]
L2[("tech_notice", "en")] = [
    "Subject: [Deprecation] {product} {ver} has been deprecated and auto-redirected\n\n{product} {ver} is now deprecated and no longer available as an independent model. All traffic is automatically redirected to {product} {ver2}. Learn more about {product} {ver2}.\n\n{foot_s}",
    "Subject: You shared some {vendor} Account data with {app}\n\nKeep track of your {vendor} Account data. If you want to stop using Sign in with {vendor} with {app}, go to your {vendor} Account. Review the Privacy Policy and Terms of Service to understand how your data is processed.\n\n{foot_s}",
]
L2[("security_ok", "en")] = [
    "Subject: New sign-in to your {vendor} account\n\nHi {name}, we noticed a new sign-in to your {vendor} account on {device}. If this was you, you do not need to do anything. If not, we will help you secure your account. Review your recent activity in your account settings.\n\n{foot_s}",
]
L2[("social", "en")] = [
    "Subject: 5 new jobs for you\n\nHi {name}, based on your profile here are new jobs matching your preferences. View jobs. Update your job preferences in your account. Get the mobile app.\n\n{foot_s}",
    "Subject: {name} viewed your profile\n\nSee who is looking at your profile and grow your network. Open the mobile app or visit {site}.\n\n{foot_s}",
]

# ---- look-alike phishing: same e-commerce footer wording, scam content ----
P2 = {}
P2[("fake_ecom", "en")] = [
    "Subject: {shop}: payment failed - account will be closed\n\nHi {name}, we could not process your last payment of Rs {amt}. Update your payment method within {hrs} hours at {fake} or your account will be closed.\n\n{foot_e}",
    "Subject: Your {shop} order cannot be delivered\n\nYour order {longorder} is on hold. Confirm your address and pay a Rs {fee} delivery fee at {fake} within {hrs} hours.\n\n{foot_e}",
    "Subject: Refund of Rs {amt} pending\n\nTo receive your refund, verify your card number, CVV and OTP at {fake}. Refund expires in {hrs} hours.\n\n{foot_e}",
]

rows += build(L2, "legitimate", 18)
rows += build(P2, "phishing", 40)

seen, out = set(), []
for r in rows:
    if r["text"] not in seen:
        seen.add(r["text"])
        out.append(r)
random.shuffle(out)

with open("indian_emails.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["text", "label", "language", "type", "source"])
    w.writeheader()
    w.writerows(out)

from collections import Counter
print(len(out), Counter(r["label"] for r in out), Counter(r["language"] for r in out))