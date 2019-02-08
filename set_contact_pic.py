import AddressBook as ab
import os
import pickle

CACHE_FILE = "cache.pkl"
BINDINGS_FILE = "bindings.pkl"

address_book = ab.ABAddressBook.sharedAddressBook()
people = address_book.people()

# TODO: Convert to class

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "rb") as cf:
        cache = pickle.load(cf)
else:
    cache = set()

if os.path.exists(BINDINGS_FILE):
    with open(BINDINGS_FILE, "rb") as bf:
        bindings = pickle.load(bf)
else:
    bindings = {}

def _find_matching_people_by_name(contact_name):
    matching_people = set()
    for p in people:
        if p.displayName() == contact_name:
            matching_people.add(p)
    return matching_people

def _find_person_by_unique_id(unique_id):
    for p in people:
        if p.uniqueId() == unique_id:
            return p
    raise ValueError("Couldn't find a person with unique_id={}".format(unique_id))

def _add_to_cache(data):
    cache.add(data)
    with open(CACHE_FILE, "wb") as cf:
        pickle.dump(cache, cf)

def _save_bindings():
    with open(BINDINGS_FILE, "wb") as bf:
        pickle.dump(bindings, bf)

def set_contact_pic(person_identifier, contact_name, pic_path, offer_change_name=False):
    if pic_path in cache:
        print "Skipping {} because already set it's picture in previous run".format(contact_name)
        return

    p = None

    if person_identifier in bindings:
        # We have an addressbook entry linked to this Facebook profile
        try:
            p = _find_person_by_unique_id(bindings[person_identifier])
        except ValueError:
            print "Couldn't find address book entry {}. Removing this binding to identifier {}".format(bindings[person_identifier], person_identifier)
            bindings.pop(person_identifier)
            _save_bindings()

    if p is None:
        matching_people = _find_matching_people_by_name(contact_name)
        
        while len(matching_people) == 0:
            print "Failed finding {}".format(contact_name)
            different_name = raw_input("If you'd like to search for this contact with a different name, type it: ")
            if len(different_name) == 0:
                return
            else:
                offer_change_name = True
                matching_people = _find_matching_people_by_name(different_name)
                if len(matching_people) == 0:
                    print "Still no person found. Try again"
        
        if len(matching_people) > 1:
            matching_people_list = list(matching_people)
            os.system("open \"{}\"".format(pic_path))
            print "Found a few matching. Please enter the index of: "
            for i, mp in enumerate(matching_people_list):
                print "#{}: {}".format(i, mp)
            matching_index_str = raw_input("What index is matching: ")
            if len(matching_index_str) == 0:
                print "Giving up on this contact"
                return
            matching_index = int(matching_index_str)
            p = matching_people_list[matching_index]
        else:
            p = list(matching_people)[0]

        bindings[person_identifier] = p.uniqueId()
        _save_bindings()

    print "Found {}".format(contact_name)
    
    if offer_change_name:
        new_name_parts = contact_name.split(" ")
        should_change_name = raw_input("Change the contact's name from {} to {}? [y/n]: ".format(p.displayName(), contact_name))
        if should_change_name.lower() in ("y", "yes"):
            if len(new_name_parts) != 2:
                print "Seting name parts manually because couldn't figure out division to <First Name> - <Middle Name> - <Last Name> automatically"
                if not p.setValue_forProperty_(raw_input("First name: "), ab.kABFirstNameProperty):
                    print "Failed to set first name"
                if not p.setValue_forProperty_(raw_input("Middle name: "), ab.kABMiddleNameProperty):
                    print "Failed to set middle name"
                if not p.setValue_forProperty_(raw_input("Last name: "), ab.kABLastNameProperty):
                    print "Failed to set last name"
            else:
                if not p.setValue_forProperty_(new_name_parts[0], ab.kABFirstNameProperty):
                    print "Failed to set first name"
                if not p.setValue_forProperty_(new_name_parts[1], ab.kABLastNameProperty):
                    print "Failed to set last name"
                
            if p.displayName() != contact_name:
                print "Changed name is different than Facebook name. Current contact name: {}. Facebook name: {}".format(p.displayName(), contact_name)
            else:
                print "Successfully changed name"
    
    print "Backing up image data"
    previous_image_data = p.imageData()

    dd = open(pic_path, "rb").read()
    d = ab.NSData.alloc().initWithBytes_length_(dd, len(dd))

    if p.setImageData_(d):
        raw_input('Before setting picture ')
        print "Success setting picture!"
        _add_to_cache(pic_path)
        address_book.save()
    else:
        print "Failed setting picture... Trying to restore"
        if p.setImageData_(previous_image_data):
            print "Restored successfully"
        else:
            print "Restore failed. Sorry"
    return
    
