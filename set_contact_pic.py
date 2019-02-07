import AddressBook as ab
import os
import pickle

CACHE_FILE = "cache.pkl"

address_book = ab.ABAddressBook.sharedAddressBook()
people = address_book.people()

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "rb") as cf:
        cache = pickle.load(cf)
else:
    cache = set()

def _find_matching_people_by_name(contact_name):
    matching_people = set()
    for p in people:
        if p.displayName() == contact_name:
            matching_people.add(p)
    return matching_people

def _add_to_cache(data):
    cache.add(data)
    with open(CACHE_FILE, "wb") as cf:
        pickle.dump(cache, cf)

def set_contact_pic(contact_name, pic_path, offer_change_name=False):
    if pic_path in cache:
        print "Skipping {} because already set it's picture in previous run".format(contact_name)
        return

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

    print "Found {}".format(contact_name)

    if offer_change_name:
        new_name_parts = contact_name.split(" ")
        if len(new_name_parts) != 2:
            print "Cannot change name since new name ({}) isn't formatted as <first name> <last name>".format(contact_name)
        else:
            should_change_name = raw_input("Change the contact's name from {} to {}? [y/n]: ".format(p.displayName(), contact_name))
            if should_change_name.lower() in ("y", "yes"):
                if not p.setValue_forProperty_(new_name_parts[0], 'First'):
                    print "Failed to set first name"
                if not p.setValue_forProperty_(new_name_parts[1], 'Last'):
                    print "Failed to set last name"
                if p.displayName() != contact_name:
                    print "Failed to change name. Current contact name: {}".format(p.displayName())
                print "Successfully changed name"
    
    print "Backing up image data"
    previous_image_data = p.imageData()

    dd = open(pic_path, "rb").read()
    d = ab.NSData.alloc().initWithBytes_length_(dd, len(dd))

    if p.setImageData_(d):
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
    
