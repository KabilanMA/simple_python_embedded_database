import os
import sys
import signal
import json
from threading import Thread

RECORD_TYPE = {'personal':1, 'sickness':2, 'drug_prescription':3, 'lab_test':4}

class Database(object):
    
    key_string_error = TypeError('Custom type error occured')
    
    def __init__(self, location, auto_dump, sig=True):
        
        self.load(location, auto_dump)
        self.dthread = None
        if sig:
            self.set_sigterm_handler()
    
    def __getitem__(self, item):
        return self.get(item)
    
    def __setitem__(self, key, value):
        return self.set(key, value)
    
    def __delitem__(self, key):
        return self.rem(key)
    
    def set_sigterm_handler(self):
        def sigterm_handler():
            if self.dthread is not None:
                self.dthread.join()
            sys.exit(0)
        signal.signal(signal.SIGTERM, sigterm_handler)
        
    def load(self, location, auto_dump):
        location = os.path.expanduser(location)
        self.loco = location
        self.auto_dump = auto_dump
        if os.path.exists(location):
            self._loaddb()
        else:
            self.db = {}
        return True
    
    def dump(self):
        self.dthread = Thread(target=json.dump, args=(self.db, open(self.loco, 'w')), kwargs={'indent':4})
        self.dthread.start()
        self.dthread.join()
        return True
    
    def _loaddb(self):
        try:
            with open(self.loco, 'r') as dataRecord:
                self.db = json.load(dataRecord)
        except ValueError:
            if os.stat(self.loco).st_size == 0:
                self.db = {}
            else:
                raise # File is not empty, avoid overwriting it
    
    def _autodumpdb(self):
        if self.auto_dump:
            self.dump()
            
    def set(self, key, value):
        if isinstance(key, str):
            self.db[key] = value
            self._autodumpdb()
            return True
        else:
            raise self.key_string_error
    
    def get(self, key):
        try:
            return self.db[key]
        except KeyError:
            return False
    
    def getAll(self):
        return self.db.keys()
    
    def exists(self, key):
        return key in self.db
    
    def rem(self, key):
        if not key in self.db:
            return False
        del self.db[key]
        self._autodumpdb()
        return True
    
    def totalkeys(self, name=None):
        if name is None:
            total = len(self.db)
            return total
        else:
            total = len(self.db[name])
            return total
    
    def append(self, key, value):
        self.db[key] = value
        self._autodumpdb()
        return True
    
    def lcreate(self, name):
        if isinstance(name, str):
            self.db[name] = []
            self._autodumpdb()
            return True
        else:
            raise self.key_string_error
        
    def ladd(self, name, value):
        self.db[name].append(value)
        self._autodumpdb()
        return True
    
    def lextend(self, name, seq):
        self.db[name].extend(seq)
        self._autodumpdb()
        return True
    
    def lgetall(self, name):
        return self.db[name]
    
    def lget(self, name, pos):
        return self.db[name][pos]
    
    def lrange(self, name, start=None, end=None):
        '''Return range of values in a list '''
        return self.db[name][start:end]

    def lremlist(self, name):
        '''Remove a list and all of its values'''
        number = len(self.db[name])
        del self.db[name]
        self._autodumpdb()
        return number

    def lremvalue(self, name, value):
        '''Remove a value from a certain list'''
        self.db[name].remove(value)
        self._autodumpdb()
        return True

    def lpop(self, name, pos):
        '''Remove one value in a list'''
        value = self.db[name][pos]
        del self.db[name][pos]
        self._autodumpdb()
        return value

    def llen(self, name):
        '''Returns the length of the list'''
        return len(self.db[name])

    def lappend(self, name, pos, more):
        '''Add more to a value in a list'''
        tmp = self.db[name][pos]
        self.db[name][pos] = tmp + more
        self._autodumpdb()
        return True

    def lexists(self, name, value):
        '''Determine if a value  exists in a list'''
        return value in self.db[name]

    def dcreate(self, name):
        '''Create a dict, name must be str'''
        if isinstance(name, str):
            self.db[name] = {}
            self._autodumpdb()
            return True
        else:
            raise self.key_string_error

    def dadd(self, name, pair):
        '''Add a key-value pair to a dict, "pair" is a tuple'''
        self.db[name][pair[0]] = pair[1]
        self._autodumpdb()
        return True

    def dget(self, name, key):
        '''Return the value for a key in a dict'''
        return self.db[name][key]

    def dgetall(self, name):
        '''Return all key-value pairs from a dict'''
        return self.db[name]

    def drem(self, name):
        '''Remove a dict and all of its pairs'''
        del self.db[name]
        self._autodumpdb()
        return True

    def dpop(self, name, key):
        '''Remove one key-value pair in a dict'''
        value = self.db[name][key]
        del self.db[name][key]
        self._autodumpdb()
        return value

    def dkeys(self, name):
        '''Return all the keys for a dict'''
        return self.db[name].keys()

    def dvals(self, name):
        '''Return all the values for a dict'''
        return self.db[name].values()

    def dexists(self, name, key):
        '''Determine if a key exists or not in a dict'''
        return key in self.db[name]

    def dmerge(self, name1, name2):
        '''Merge two dicts together into name1'''
        first = self.db[name1]
        second = self.db[name2]
        first.update(second)
        self._autodumpdb()
        return True

    def deldb(self):
        '''Delete everything from the database'''
        self.db = {}
        self._autodumpdb()
        return True
    
    def patientGetRecordDetails(self, user_id, detailType):
        output = []
        for key in self.db:
            try:
                temp_data = self.db[key]
                if(temp_data['patient_id'] == user_id and temp_data['record_type'] == RECORD_TYPE[detailType] and temp_data['sens_level'] >=3):
                    output.append(temp_data)
            except KeyError:
                print("Something wrong with the data structure, please reset the record.db database")
                continue
            
        return output
    
    def staffGetRecord(self, staff_type, record_type, username='', user_id=''):
        output = []
        
        if username !='':
            for key in self.db:
                try:
                    temp_data = self.db[key]
                    if(temp_data['patient_name'] == username and temp_data['record_type'] == RECORD_TYPE[record_type]):
                        if (user_id != '' and temp_data['patient_id'] == user_id):
                            raise self.key_string_error
                            
                        if staff_type == 1:
                            print("Patients can't view this")
                            return []
                        elif staff_type > 100:
                            output.append(temp_data)
                        elif staff_type >1 and staff_type<100:
                            if(temp_data['sens_level']>1 and temp_data['sens_level'] !=3):
                                output.append(temp_data)
                        else:
                            return []
                except KeyError as e:
                    print("Something went wrong: {}".format(e.__str__()))
                    continue
                
                except TypeError as e:
                    print("Something went wrong: {}".format(e.__str__()))
                    continue
                
            return output
        
        if user_id != '':
            for key in self.db:
                try:
                    temp_data = self.db[key]
                    if(temp_data['patient_id'] == user_id and temp_data['record_type'] == RECORD_TYPE[record_type]):
                        if (username != '' and temp_data['patient_name'] == user_id):
                            raise self.key_string_error
                            
                        if staff_type == 1:
                            print("Patients can't view this")
                            return []
                        elif staff_type > 100:
                            output.append(temp_data)
                        elif staff_type >1 and staff_type<100:
                            if(temp_data['sens_level']>1 and temp_data['sens_level'] !=3):
                                output.append(temp_data)
                        else:
                            return []
                except KeyError as e:
                    print("Something went wrong: {}".format(e.__str__()))
                    continue
                
                except TypeError as e:
                    print("Something went wrong: {}".format(e.__str__()))
                    continue
                
            return output
        
        if user_id == '' and username == '':
            for key in self.db:
                try:
                    temp_data = self.db[key]
                    if(temp_data['record_type'] == RECORD_TYPE[record_type]): 
                        if staff_type == 1:
                            print("Patients can't view this")
                            return []
                        elif staff_type > 100:
                            output.append(temp_data)
                        elif staff_type >1 and staff_type<100:
                            if(temp_data['sens_level']>1 and temp_data['sens_level'] !=3):
                                output.append(temp_data)
                        else:
                            return []
                except KeyError as e:
                    print("Something went wrong: {}".format(e.__str__()))
                    continue
                except TypeError as e:
                    print("Something went wrong: {}".format(e.__str__()))
                    continue
            return output
        return output
    
                 