import hashlib
import json
import os
import uuid

from Database import Database

def getUserInput():
    userName = input("Enter the username: ").strip()
    password = input("Enter your password: ").strip()
    
    return userName, password

def readUser(username):
    s = "{\"username}"

def writeUserData(id, type, username, password, designation):
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    jsonDataToStore = {"id":id, "type":type,"username":username, "password":password, "designation":designation}
    
    with open('config.json','r') as jsonConfigFile:
        try:
            users = json.load(jsonConfigFile)
        except json.decoder.JSONDecodeError:
            users = []
            
    for user in users:
        if user['username'] == username and user['id'] == id:
            return False
    
    users.append(jsonDataToStore)
    with open('config.json','w') as jsonConfigFile:
        json.dump(users, jsonConfigFile, indent=4)
        return True
        
    
def validate(userName, password):
    with open("config.json","r") as jsonfile:
        users = json.load(jsonfile)
    if not jsonfile.closed:
        jsonfile.close()
                
    for user in users:
        if user['username'] == userName:
            configPassword = user['password']
            break
    else:
        # no such user in the config file
        return -1,-1

    if(hashlib.md5(password.encode('utf-8')).hexdigest() == configPassword):
        # username and password matches
        return user['type'], user['id']
    #password didn't match
    return -1,-1

def exitApplication(option):
    print("\nExiting the application...\n")
    os._exit(1)   

def printPrettier(datas):
    if len(datas) == 0:
        print("<No records>")
        return 0
    for index, data in enumerate(datas):
        print("Data {}:\n\t".format(index+1))
        for key in data:
            if (key == 'record_type' or key == 'sens_level'):
                continue
            tab='\t'
            if len(key) < 5:
                tab='\t\t'
                
            output = "\t" + str(key) + tab +"--> "+ str(data[key])
            print(output)
    return 1
            
def userProcess(userType, username, user_id, password):
    global db
    if(userType == 1):
        # patient
        # can read only his record of all category
        # cannot write any record
        SELECTION_OPTION = {'1':'personal','2':'sickness', '3':'drug_prescription', '4':'lab_test'}
        
        selection = input("\nPlease  enter only the relevant integer preceding the options to make choice.\nYou can view your records.\n1. View Personal Details.\n2. View All Sickness Details.\n3. View All Drug Prescription Details.\n4. View All Lab Test Prescription Details.\n")

        # authentication before fetching the actual data
        try:
            temp_userType, temp_user_id = validate(username, password)
            if(temp_userType > 0 and temp_userType < 6 and temp_userType == userType and user_id == temp_user_id):
                personalDetails = db.patientGetRecordDetails(user_id, SELECTION_OPTION[selection])
                                
                if len(personalDetails)==0:
                    return 0
                else:
                    printPrettier(personalDetails)
                    return 1
            else:
                return -1
        
        except KeyError:
            print("Key Error!")
            return -1
        
    elif userType > 1 and userType < 101:
        SELECTION_OPTION = {'1':'personal','2':'sickness', '3':'drug_prescription', '4':'lab_test'}
        selection = input("\nPlease  enter only the relevant integer preceding the options to make choice.\n1. View patient personal details.\n2. View patient sickness details.\n3. Record new patient-detail\n")
        
        if selection == '1' or selection == '2':
            selection_2 = input("\nSelect patient using;\n1. User ID\n2. Username\n3. All\n")
            
            output = []
            
            if selection_2 == '1':
                patient_id = (input("Enter user ID: ")).strip()
                output = db.staffGetRecord(userType, SELECTION_OPTION[selection], user_id=patient_id)
            
            elif selection_2 == '2':
                patient_name = (input("Enter username: ")).strip()
                output = db.staffGetRecord(userType, SELECTION_OPTION[selection], username=patient_name)
            
            elif selection_2 == '3':
                output = db.staffGetRecord(userType, SELECTION_OPTION[selection])
            else:
                return -1
            
            if len(output) == 0:
                return 0    
            printPrettier(output)
            return 1
        
        elif selection == '3':
            try:
                patient_id = input("Enter Patient ID: ").strip()
                patient_name = input("Enter Patient Name: ").strip()
                record_type = SELECTION_OPTION[input("\nSelect Record Type Using the Index Below:\n1. Personal Details.\n2. Sickness Details.\n3. Drug Prescription Details.\n4. Lab Test Details.\n\t:")]
                
                data = input("Enter the relevant data record: ")
                
                sens_level = int(input("\nWhat is the sensitivity level of the data:\n1. Only the doctor can view.\n2. Hospital staffs including the doctor san view.\n3. Only the doctor and relevant patient can view.\n4. Any using the system can view.\n\t:"))
                if (sens_level<1 or sens_level>4):
                    raise KeyError
                
                record = {"patient_id": patient_id, "patient_name":patient_name, "record_type":record_type, "sens_level":sens_level,"data":data}
                
                test1 = writeUserData(patient_id.strip(), 1, patient_name.strip(), password.strip(), 'patient')
                test2 = db.append('{}'.format(uuid.uuid1()), record)
                
                if test1 and test2:
                    print("\nSuccesfully updated users and records")
                    return 1
                else:
                    print("\nEither users or the records are not updated")
                    return 0
                
            except KeyError:
                print("KEY ERROR!")
                return -1
            except ValueError:
                print("KEY ERROR!")
                return -1
        
    
    # elif userType > 100 and userType < 250:
        
            
                
                
if __name__ == "__main__":
    isLoggedin = False
    userType = -1
    global db
    db = Database('record.db', True)
    try:
        print('Press ctrl+C to exit the application at any point')
        while True:
            if not isLoggedin:
                username, password = getUserInput()
                userType, user_id = validate(username, password)
                if(userType>0):
                    isLoggedin = True
                    print("Successfully logged in as "+ username)
                else:
                    isLoggedin = False
                    print("Invalid Username or Password")
                continue
            else:
                if (userType < 0) or (userType>5):
                    print("Invalid Access Denied. Login again to authenticate")
                    continue
                else:
                    userProcess(userType, username, user_id, password)
                
    except KeyboardInterrupt:
        exitApplication('s')
        