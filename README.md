# Marketing Analytics Dashboard

Αυτό είναι ένα απλό **Marketing Analytics Dashboard** φτιαγμένο με [Streamlit](https://streamlit.io/) για την οπτικοποίηση KPIs από διάφορα διαφημιστικά κανάλια.

---

## Περιεχόμενα

- `dashboard.py`: Το κύριο αρχείο της εφαρμογής Streamlit.
- `data/marketing_data.csv`: Δείγμα mock δεδομένων με impressions, clicks, conversions, κόστος κ.ά.
- `requirements.txt`: Οι απαραίτητες βιβλιοθήκες Python.

---

## Οδηγίες Εκτέλεσης

### Τοπικά

**1. Κλωνοποίησε το αποθετήριο:**
git clone https://github.com/το-username-sou/marketing-dashboard.git

**2. Μετακινήσου στον φάκελο:**
cd marketing-dashboard

**3. Δημιούργησε και ενεργοποίησε ένα virtual environment (προαιρετικά):**
python -m venv venv
source venv/bin/activate # Linux/Mac
venv\Scripts\activate # Windows

**4. Εγκατάστησε τις βιβλιοθήκες:**
pip install -r requirements.txt

**5. Τρέξε το dashboard:**

### Στο Streamlit Cloud

1. Ανέβασε το repo στο GitHub.
2. Πήγαινε στο [Streamlit Cloud](https://streamlit.io/cloud) και σύνδεσε το GitHub repo.
3. Κάνε deploy επιλέγοντας το `dashboard.py` ως αρχείο εκκίνησης.

---

## Περιγραφή Δεδομένων

Το αρχείο `marketing_data.csv` περιλαμβάνει τα εξής πεδία:

| Πεδίο       | Περιγραφή                     |
|-------------|------------------------------|
| channel     | Το διαφημιστικό κανάλι        |
| impressions | Αριθμός εμφανίσεων            |
| clicks      | Αριθμός κλικς                |
| conversions | Αριθμός μετατροπών           |
| cost        | Κόστος διαφήμισης σε ευρώ    |
| ctr         | Click-through rate (%)       |
| cpa         | Κόστος ανά μετατροπή (CPA)   |

---

## Άδειες Χρήσης

Το project είναι ελεύθερο για χρήση και τροποποίηση.

---

## Επικοινωνία

Για ερωτήσεις ή βελτιώσεις, μπορείς να ανοίξεις issue στο GitHub repo.

---

Καλή διασκέδαση με το dashboard! 🚀
