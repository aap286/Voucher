# required dependencies
from flask import Flask, render_template, request
import os, locale, webview, csv, json
from cryptography.fernet import Fernet
from num2words import num2words
from datetime import datetime


# ? key
key = b"zjjUTUFB3ONwdx3iD8rbOEj9DrC-Mw0Hfihg0EUkl3U="
cipher = Fernet(key)

# ? Set the desired locale for India
locale.setlocale(locale.LC_ALL, "en_IN")

# ! function


# TODO: opens and reads file
def extractData(storageArray, filepath, openType):
    completeFilepath = "{}".format(filepath)

    textFile = open(completeFilepath, openType)

    textFile.seek(0)
    lines = textFile.readlines()

    if os.path.getsize(filepath) != 0:
        storageArray.clear()
        for line in lines:
            storageArray.append(line.rstrip("\n"))

    textFile.close()


# TODO: creates folder and file
def createFolder(foldername, files):
    if not os.path.exists(foldername):
        # Create the folder
        os.makedirs(foldername)
    else:
        print(f"Folder '{foldername}' already exists. Skipping folder creation.")
    for filename in files:
        filepath = os.path.join(foldername, f"{filename}")
        # Check if the file exists
        if not os.path.exists(filepath):
            with open(filepath, "w") as file:
                pass
        else:
            print(f"File '{filepath}' already exists. Skipping file creation.")


# TODO: increments serial number if key exists else makes a new key
def increment(file_path, arr):
    payType = {"Cash": ["CSH", 100000], "Cheque": ["CHQ", 200000], "NEFT": ["NFT", 300000]}
    form_date = datetime.strptime(arr[2], "%d/%m/%Y")

    with open(file_path, "rb") as file:
        file_content = file.read()
        if file_content != b"":
            decryptDict = json.loads(cipher.decrypt(file_content).decode())
        else:
            decryptDict = {}

    yearSelected = payType[arr[6]][0] + (
        str(form_date.year + 1) if form_date.month >= 4 else str(form_date.year)
    )

    decryptDict[yearSelected] = decryptDict.get(yearSelected, payType[arr[6]][1] ) + 1

    with open(file_path, "wb") as file:
        file.write(cipher.encrypt(json.dumps(decryptDict).encode()))

    arr[0] = "{}/{}/{}".format(payType[arr[6]][0], decryptDict[yearSelected], yearRange(form_date))


#  TODO: returns the year range
def yearRange(date):
    month = date.month
    year = date.year
    if month < 4:
        year -= 1

    return "{}-{}".format(year, str(year + 1)[-2:])


# TODO: converts date format
def dateFormat(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")


# ! create folders and files just in case
configuration = ["debits.txt", "bankNames.txt", "conveyer.txt"]
database = ["dataRepository.txt"]
SecureArchive = ["encryptedData.txt"]


createFolder("⚙️ Configuration", configuration)
createFolder("🗄️ Database", database)
createFolder("🔒 SecureArchive", SecureArchive)

# ! file paths
encrypt_path = "🔒 SecureArchive/{}".format(SecureArchive[0])
configuration_file_path = [
    "⚙️ Configuration/{}".format(filename) for filename in configuration
]
file_path_db = "🗄️ Database/{}".format(database[0])


# ! setup

# ? retrieve value for dropdown
debiteAccounts = ["Plan 1", "Plan 2", "Plan 3"]
bankNames = [
    "JPMorgan Chase Bank",
    "Bank of America",
    "Citibank",
    "PNC Bank",
]
conveyers = ["Iternary 1", "Iternary 2", "Iternary 3"]

extractData(debiteAccounts, configuration_file_path[0], "r")
extractData(bankNames, configuration_file_path[1], "r")
extractData(conveyers, configuration_file_path[2], "r")

# ? column names for database
if os.path.getsize(file_path_db) == 0:
    colnames = "No\t Debit A/c\t  Date\t Pay to\t Rs. (In digits)\t Rs. (In words)\t Payment type\t Cheque Number\t Dated\t Bank Name\t Conveyer\t Being"
    with open(file_path_db, "w") as file:
        file.write(colnames + "\n")


# initialize app
def intializeApp():
    app = Flask(
        __name__, template_folder="assets/templates", static_folder="assets/style"
    )
    window = webview.create_window("Voucher", app, width=700, height=800)

    # TODO: Handling error
    @app.errorhandler(Exception)
    def handle_error():
        return render_template("error.html")

    # TODO: Displays form
    @app.route("/", methods=["GET"])
    def form():
        return render_template(
            "form.html",
            debitDropdown=debiteAccounts,
            bankNames=bankNames,
            conveyers=conveyers,
        )

    #  TODO: Displays on submission
    @app.route("/submission", methods=["POST"])
    def submission():
        userStorage = [0]
        userStorage.append(request.form.get("Debit"))

        userStorage.append(request.form.get("Date"))
        userStorage[-1] = dateFormat(userStorage[-1])

        userStorage.append(request.form.get("Pay"))

        number = int(request.form.get("Price"))
        userStorage.append(str(locale.format_string("%d", number, grouping=True)))
        userStorage.append(
            num2words(request.form.get("Price"), lang="en_IN", to="cardinal") + " only"
        )

        userStorage.append(request.form.get("paymentType"))
        if userStorage[-1] == "Cheque":
            userStorage.append(request.form.get("chequeNo"))
            userStorage.append(request.form.get("Dated"))
            userStorage[-1] = dateFormat(userStorage[-1])
            userStorage.append(request.form.get("bankName"))
        else:
            userStorage.append("-")
            userStorage.append("-")
            userStorage.append("-")

        userStorage.append(request.form.get("conveyer"))
        userStorage.append(request.form.get("Being"))

        # print(userStorage[2])
        increment(encrypt_path, userStorage)

        with open(file_path_db, "a", newline="") as file:
            writer = csv.writer(file, delimiter="\t")
            writer.writerows([userStorage])

        return render_template("voucher.html", data=userStorage)

    if __name__ == "__main__":
        # app.run(debug=True)
        webview.start()


# ! runs app
intializeApp()
