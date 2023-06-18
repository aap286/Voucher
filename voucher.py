# required dependencies
from flask import Flask, render_template, request
from cryptography.fernet import Fernet
from num2words import num2words
import os, locale, webview, csv

# ? key
key = b"zjjUTUFB3ONwdx3iD8rbOEj9DrC-Mw0Hfihg0EUkl3U="
cipher = Fernet(key)

# ? Set the desired locale for India
locale.setlocale(locale.LC_ALL, "en_IN")

# ! function


# TODO: opens and reads file
def extractData(storageArray, filepath, openType, encryption_key=False):
    # Entire file path
    completeFilepath = "{}".format(filepath)

    # Open the text file
    textFile = open(completeFilepath, openType)

    # Read line by line
    textFile.seek(0)  # Reset the file pointer to the beginning
    lines = textFile.readlines()

    if encryption_key:
        # Handle encrypted file
        for line in lines:
            decrypted_data = cipher.decrypt(line)
            storageArray.append(decrypted_data.decode())

    elif os.path.getsize(filepath) != 0:
        storageArray.clear()
        # File is not empty, append data to the storage array
        for line in lines:
            storageArray.append(line.rstrip("\n"))

    textFile.close()  # Close the file


# TODO: stores encrypted data
def storeEncryptedData(data):
    # encode data
    encryptedData = cipher.encrypt(data.encode())
    # file path
    file_path = "SecureArchive/encryptedData.trouve"
    with open(file_path, "wb") as file:
        file.write(encryptedData + b"\n")


# TODO: creates folder and file
def createFolder(foldername, files):
    # Check if the folder exists
    if not os.path.exists(foldername):
        # Create the folder
        os.makedirs(foldername)

        for filename in files:
            filepath = os.path.join(foldername, f"{filename}")

            # Check if the file exists
            if not os.path.exists(filepath):
                # Create an empty file
                with open(filepath, "w") as file:
                    pass
            else:
                print(f"File '{filepath}' already exists. Skipping file creation.")

    else:
        print(f"Folder '{foldername}' already exists. Skipping folder creation.")


# ! create folders and files just in case
configuration = ["bankNames.txt", "conveyer.txt", "debits.txt"]
database = ["dataRepository.txt"]
SecureArchive = ["encryptedData.trouve"]

createFolder("configuration", configuration)
createFolder("database", database)
createFolder("SecureArchive", SecureArchive)

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

extractData(debiteAccounts, "configuration/debits.txt", "r")
extractData(bankNames, "configuration/bankNames.txt", "r")
extractData(conveyers, "configuration/conveyer.txt", "r")

# ? column names for database
database_filepath = "database/{}".format(database[0])
if os.path.getsize(database_filepath) == 0:
    colnames = "No\t Debit A/c\t  Date\t Pay to\t Rs. (In digits)\t Rs. (In words)\t Payment type\t Cheque Number\t Dated\t Bank Name\t Conveyer\t Being"
    with open(database_filepath, "w") as file:
        file.write(colnames + "\n")

# initialize app
def intializeApp():
    app = Flask(
        __name__, template_folder="assets/templates", static_folder="assets/style"
    )
    window = webview.create_window("Voucher", app, width=1000, height=950)

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
        # * get the latest encrypted number
        decryptedData = []
        extractData(decryptedData, "SecureArchive/encryptedData.trouve", "rb", True)

        # if encrytion data is empty
        num = (
            lambda decryptedData: int(decryptedData[-1])
            if len(decryptedData) != 0
            else 999999
        )(decryptedData)

        # * resets user data
        userStorage = [num + 1]

        userStorage.append(request.form.get("Debit"))
        userStorage.append(request.form.get("Date"))
        userStorage.append(request.form.get("Pay"))
        number = int(request.form.get("Price"))
        userStorage.append(str(locale.format_string("%d", number, grouping=True)))
        userStorage.append(
            num2words(request.form.get("Price"), lang="en_IN", to="cardinal")
        )
        userStorage.append(request.form.get("paymentType"))

        # checks payment type
        if userStorage[-1] == "Cheque":
            userStorage.append(request.form.get("chequeNo"))
            userStorage.append(request.form.get("Dated"))
            userStorage.append(request.form.get("bankName"))
        else:
            userStorage.append("-")
            userStorage.append("-")
            userStorage.append("-")

        userStorage.append(request.form.get("conveyer"))
        userStorage.append(request.form.get("Being"))

        # * add information to encryption file
        storeEncryptedData(str(userStorage[0]))
    
        # storing string in database
        file_path_db = "database/dataRepository.txt"
        with open(file_path_db, "a", newline="") as file:
            writer = csv.writer(file, delimiter="\t")
            writer.writerows([userStorage])

        return render_template("voucher.html", data=userStorage)

    if __name__ == "__main__":
        app.run(debug=False)
        # webview.start()


# ! runs app
intializeApp()
