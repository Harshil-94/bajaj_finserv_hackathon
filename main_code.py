# %%
import pandas as pd
import json

# Load JSON data
with open('./DataEngineeringQ2.json') as file:
    json_data = file.read()

# Parse JSON data
data = json.loads(json_data)

# Extract required columns from JSON data
appointments = []
for item in data:
    patient_details = item['patientDetails']
    gender = patient_details.get('gender', None)
    birth_date = patient_details.get('birthDate', None)
    appointment = {
        'appointmentId': item['appointmentId'],
        'phoneNumber': item['phoneNumber'],
        'firstName': patient_details['firstName'],
        'lastName': patient_details['lastName'],
        'gender': gender if gender in ['M', 'F'] else None,
        'DOB': birth_date,
        'medicines': item['consultationData']['medicines']
    }
    appointments.append(appointment)

# Create DataFrame from extracted data
df = pd.DataFrame(appointments)


# %%
df.head()

# %%
df.columns

# %%
df["fullName"] = df["firstName"] + " " + df["lastName"]

# %%
def is_valid_mobile(number):
    if number is None:
        return False
    number = str(number)
    if number.startswith("+91"):
        number = number[3:]
    elif number.startswith("91"):
        number = number[2:]
    return number.isdigit() and 6000000000 <= int(number) <= 9999999999


df["isValidMobile"] = df["phoneNumber"].apply(is_valid_mobile)

# %%
import hashlib
#hasing the column 
def hash_phone_number(number):
    if number is None or not is_valid_mobile(number):
        return None
    number = str(number)
    if number.startswith("+91"):
        number = number[3:]
    elif number.startswith("91"):
        number = number[2:]
    return hashlib.sha256(number.encode()).hexdigest()

df["phoneNumberHash"] = df["phoneNumber"].apply(hash_phone_number)

# %%
def calculate_age(birth_date):
    if birth_date is None:
        return None
    birth_date = pd.to_datetime(birth_date)
    today = pd.Timestamp.now()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age

df["Age"] = df["DOB"].apply(calculate_age)

# %%
df['medicines'][0] # checking the medicines column details

# %%
# Aggregating columns by appointmentId
df["noOfMedicines"] = df["medicines"].apply(lambda x: len(x))
df["noOfActiveMedicines"] = df["medicines"].apply(lambda x: sum(1 for med in x if med["isActive"]))
df["noOfInActiveMedicines"] = df["medicines"].apply(lambda x: sum(1 for med in x if not med["isActive"]))
df["MedicineNames"] = df["medicines"].apply(lambda x: ", ".join(med["medicineName"] for med in x if med["isActive"]))

# Remove the 'medicines' column if not needed
# df = df.drop("medicines", axis=1)


# %%
df_csv=df[['appointmentId','fullName','phoneNumber','isValidMobile','phoneNumberHash','gender','DOB','Age','noOfMedicines','noOfActiveMedicines','noOfInActiveMedicines','MedicineNames']]

# %%
df_csv.to_csv("output.csv", sep="~", index=False)
#saving in csv with "~" operator

# %%
df_json = df_csv.astype(object)
df_json["phoneNumber"] = df_json["phoneNumber"].astype(str) 

# %%
aggregated_data = {
    "Age": df_json["Age"].mean(),
    "gender": df_json["gender"].value_counts().to_dict(),
    "validPhoneNumbers": df_json["isValidMobile"].sum(),
    "appointments": len(df_json),
    "medicines": df_json["noOfMedicines"].sum(),
    "activeMedicines": df_json["noOfActiveMedicines"].sum()
}

# %%
with open("Aggregated_Data.json", "w") as file:
    json.dump(aggregated_data, file, indent=4)
#saving the json file

# %%
import matplotlib.pyplot as plt
gender_counts = df['gender'].value_counts(dropna=False)

# Plot the pie chart
plt.figure(figsize=(6, 6))
gender_counts.plot(kind='pie', autopct='%1.1f%%', colors=['blue', 'red', 'green'])
plt.title('Gender Distribution')
plt.legend(labels=gender_counts.index, loc='best')
plt.axis('equal')
plt.show()


