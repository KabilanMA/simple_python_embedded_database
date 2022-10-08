import hashlib
import json
import sys, os
import uuid

from Database import Database

def getUserInput():
    userName = input("Enter the username: ").strip()
    password = input("Enter your password: ").strip()
    
    return userName, password

def readUser(username):
    s = "{\"username}"

def writeUserData(username, password, privilege):
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    jsonDataToStore = {"username":username, "password":password, "privilege": privilege}
    
    with open('config.json','r') as jsonConfigFile:
        try:
            users = json.load(jsonConfigFile)
            print(users)
        except json.decoder.JSONDecodeError:
            users = []
            
    for user in users:
        if user['username'].strip() == username.strip():
            return False
        
    with open('config.json','w') as jsonConfigFile:
        users.append(jsonDataToStore)
        json.dump(users, jsonConfigFile)
        return True
        
    
def valid(userName, password):
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
        return [-1]

    if(hashlib.md5(password.encode('utf-8')).hexdigest() == configPassword):
        # username and password matches
        return user['privilege']
    #password didn't match
    return [-1]

def exitApplication(option):
    print("\nExiting the application...\n")
    os._exit(1)   
    
def getOperationOptions():
    print("Select what operation you wants to do!")
    
if __name__ == "__main__":
    db = Database('record.db', False)
    d = '{}'.format(uuid.uuid1())
    db.set(d,{"privilege_level": 1, "type":"","Data": "KABILAN IS THE ONE"})
    # db.append('name',' Mahathevan')
    db.dump()
    # writeUserData('James', 'password',[2000, 2200])
    # print(valid('kabilan', 'password'))
    # try:
    #     print("Press ctrl+C to exit the application at any point")
        
    #     while True:
    #         isLoggedin = False
    #         if not isLoggedin:
    #             userName, password = getUserInput()
    #             if (valid(userName, password)):
    #                 isLoggedin = True
    #                 print('Logged In as '+ userName)
    #             else:
    #                 temp_option = input("Invalid username or password. Want to retry?(y/n): ")
    #                 if((temp_option.strip().lower() =='y' and len(temp_option) == 1) or (temp_option.strip().lower() == 'yes' and len(temp_option) == 3)):
    #                     continue
    #                 elif((temp_option.strip().lower() =='n' and len(temp_option) == 1) or (temp_option.strip().lower() == 'no' and len(temp_option) == 3)):
    #                     exitApplication(1)
                
    # except KeyboardInterrupt:
    #     exitApplication(2)
        
