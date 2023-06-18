# required dependencies
from flask import Flask, render_template, request
import os
from cryptography.fernet import Fernet
from num2words import num2words
import webview

# ? key
key = b"zjjUTUFB3ONwdx3iD8rbOEj9DrC-Mw0Hfihg0EUkl3U="
cipher = Fernet(key)

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
    file_path = "SecureArchive/encryptedData.txt"
    with open(file_path, "ab") as file:
        file.write(encryptedData + b"\n")


# TODO: creates folder and file
def createFolder(foldername, files):
    # Check if the folder exists
    if not os.path.exists(foldername):
        # Create the folder
        os.makedirs(foldername)

        for filename in files:
            filepath = os.path.join(foldername, f"{filename}.txt")

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
configuration = ["bankNames", "conveyer", "debits"]
database = ["dataRepository"]
SecureArchive = ["encryptedData"]

createFolder("configuration", configuration)
createFolder("database", database)
createFolder("SecureArchive", SecureArchive)

# ! setup

# ? retrieve value for dropdown
debiteAccounts = ["item1", "item2", "item3"]
bankNames = ["Axis Bank", "Bank of India", "HDFC Bank", "ICIC Bank"]
conveyers = ["iternary1", "iternary2", "iternary3"]

extractData(debiteAccounts, "configuration/debits.txt", "r")
extractData(bankNames, "configuration/bankNames.txt", "r")
extractData(conveyers, "configuration/conveyer.txt", "r")


# initialize app
def intializeApp():
    app = Flask(__name__, template_folder="templates", static_folder="style")
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
        extractData(decryptedData, "SecureArchive/encryptedData.txt", "rb", True)

        # ! check previous encrypted number
        # print("List of all encrypted numbers \n {}".format(decryptedData))

        # if encrytion data is empty
        num = (
            lambda decryptedData: int(decryptedData[-1])
            if len(decryptedData) != 0
            else 999
        )(decryptedData)

        # * resets user data
        userStorage = [num + 1]

        # * add information to encryption file
        storeEncryptedData(str(userStorage[-1]))

        userStorage.append(request.form.get("Debit"))
        userStorage.append(request.form.get("Date"))
        userStorage.append(request.form.get("Pay"))
        userStorage.append(request.form.get("Price"))
        userStorage.append(
            num2words(request.form.get("Price"), lang="en_IN", to="cardinal")
        )
        userStorage.append(request.form.get("paymentType"))

        # checks payment type
        if userStorage[-1] == "Cheque":
            userStorage.append(request.form.get("Dated"))
            userStorage.append(request.form.get("bankName"))
            userStorage.append(request.form.get("chequeNo"))

        userStorage.append(request.form.get("conveyer"))
        userStorage.append(request.form.get("Being"))

        # adds information to database
        userString = ""
        for info in userStorage:
            userString = userString + str(info) + "\t"

        # storing string in database
        file_path_db = "database/dataRepository.txt"
        with open(file_path_db, "a") as file:
            file.write(userString + "\n")

        return render_template("voucher.html", data=userStorage)

    if __name__ == "__main__":
        app.run(debug=True)
        # webview.start()


# ! runs app
intializeApp()
