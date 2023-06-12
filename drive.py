# required dependencies
from flask import Flask, render_template, request
import os
from cryptography.fernet import Fernet
from num2words import num2words
import webview

# ? key
# Generate a key for encryption
key = b"zjjUTUFB3ONwdx3iD8rbOEj9DrC-Mw0Hfihg0EUkl3U="
# Create a Fernet cipher instance with the key
cipher = Fernet(key)

# ! function


# TODO: opens and reads file
def extractData(storageArray, filepath, openType, encryption_key=False):
    # Entire file path
    completeFilepath = "{}/{}".format(os.path.dirname(__file__), filepath)

    # Open the text file
    textFile = open(completeFilepath, openType)

    # Read line by line
    textFile.seek(0)  # Reset the file pointer to the beginning
    lines = textFile.readlines()
    for line in lines:
        if encryption_key:
            decrypted_data = cipher.decrypt(line)
            storageArray.append(decrypted_data.decode())
        else:
            storageArray.append(line.rstrip("\n"))

    # Close the file
    textFile.close()


# TODO: stores encrypted data
def storeEncryptedData(data):
    # encode data
    encryptedData = cipher.encrypt(data.encode())
    # file path
    file_path = "{}/SecureArchive/encryptedData.txt".format(os.path.dirname(__file__))
    with open(file_path, "ab") as file:
        file.write(encryptedData + b"\n")


# ! setup

# ? retrieve value for debit dropdown
debitDropdownValue = []  # stores value for debit dropdown
extractData(debitDropdownValue, "configuration/debits.txt", "r")

# ? stores available bank names
bankNames = []
extractData(bankNames, "configuration/bankNames.txt", "r")

# number = 1000405060
# number_in_words = num2words(number)

# print(number_in_words)


# initialize app
def intializeApp():
    app = Flask(__name__, template_folder="templates", static_folder="style")
    window = webview.create_window("Voucher", app, width=1000, height=950)

    # TODO: Displays form
    @app.route("/", methods=["GET"])
    def form():
        return render_template(
            "form.html", debitDropdown=debitDropdownValue, bankNames=bankNames
        )

    #  TODO: Displays on submission
    @app.route("/submission", methods=["POST"])
    def submission():
        # * get the latest encrypted number
        decryptedData = []
        extractData(decryptedData, "SecureArchive/encryptedData.txt", "rb", True)

        # ! check previous encrypted number
        print("List of all encrypted numbers \n {}".format(decryptedData))

        # if encrytion data is empty
        num = (
            lambda decryptedData: int(decryptedData[-1])
            if len(decryptedData) != 0
            else 0
        )(decryptedData)

        # * handle user's data
        userStorage = [num + 1]

        # * add information to encryption file
        storeEncryptedData(str(userStorage[-1]))

        userStorage.append(request.form.get("Debit"))
        userStorage.append(request.form.get("Date"))
        userStorage.append(request.form.get("Pay"))
        userStorage.append(
            num2words(request.form.get("Price"), lang="en_IN", to="cardinal"))
        userStorage.append(request.form.get("paymentType"))

        # checks payment type
        if userStorage[-1] == "Cheque":
            userStorage.append(request.form.get("Dated"))
            userStorage.append(request.form.get("bankName"))

        userStorage.append(request.form.get("Being"))

        return render_template("voucher.html", data=userStorage)

    if __name__ == "__main__":
        # app.run(debug=True)
        webview.start()


# ! runs app
intializeApp()
