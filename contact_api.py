import AddressBook
import os
import pickle

CACHE_FILE = os.path.join(os.path.dirname(__file__), "cache.pkl")
BINDINGS_FILE = os.path.join(os.path.dirname(__file__), "bindings.pkl")

class ContactAPI(object):
    def __init__(self):
        self.cache = ContactAPI._load_pickle(CACHE_FILE, set())
        self.bindings = ContactAPI._load_pickle(BINDINGS_FILE, dict())

        self.address_book = AddressBook.ABAddressBook.sharedAddressBook()
        self.people = self.address_book.people()

    @staticmethod
    def _load_pickle(pickle_file, default=None):
        if os.path.exists(pickle_file):
            with open(pickle_file, "rb") as pf:
                return pickle.load(pf)
        else:
            return default

    def _find_matching_people_by_name(self, contact_name):
        matching_people = set()
        for p in self.people:
            if p.displayName() == contact_name:
                matching_people.add(p)
        return matching_people

    def _find_person_by_unique_id(self, unique_id):
        for p in self.people:
            if p.uniqueId() == unique_id:
                return p
        raise ValueError("Couldn't find a person with unique_id={}".format(unique_id))

    def _add_to_cache(self, data):
        self.cache.add(data)
        with open(CACHE_FILE, "wb") as cf:
            pickle.dump(self.cache, cf)

    def _save_bindings(self):
        with open(BINDINGS_FILE, "wb") as bf:
            pickle.dump(self.bindings, bf)

    def _get_person_from_bindings(self, person_identifier):
        if person_identifier in self.bindings:
            # We have an addressbook entry linked to this Facebook profile
            try:
                return self._find_person_by_unique_id(self.bindings[person_identifier])
            except ValueError:
                print "Couldn't find address book entry {}. Removing this binding to identifier {}".format(bindings[person_identifier], person_identifier)
                bindings.pop(person_identifier)
                self._save_bindings()
        return None

    @staticmethod
    def _change_address_book_name_property(person, key, value):
        if not person.setValue_forProperty_(value, key):
            print "Failed to set {} name".format(key)

    def _change_contact_name(self, person, new_name):
        new_name_parts = new_name.split(" ")
        should_change_name = raw_input("Change the contact's name from {} to {}? [y/n]: ".format(person.displayName(), new_name))
        if should_change_name.lower() in ("y", "yes"):
            if len(new_name_parts) != 2:
                print "Seting name parts manually because couldn't figure out division to <First Name> - <Middle Name> - <Last Name> automatically"
                ContactAPI._change_address_book_name_property(person, AddressBook.kABFirstNameProperty, raw_input("First name: "))
                ContactAPI._change_address_book_name_property(person, AddressBook.kABMiddleNameProperty, raw_input("Middle name: "))
                ContactAPI._change_address_book_name_property(person, AddressBook.kABLastNameProperty, raw_input("Last name: "))
            else:
                ContactAPI._change_address_book_name_property(person, AddressBook.kABFirstNameProperty, new_name_parts[0])
                ContactAPI._change_address_book_name_property(person, AddressBook.kABLastNameProperty, new_name_parts[1])
                
            if person.displayName() != new_name:
                print "Changed name is different than requested. Current contact name: {}. Requested name: {}".format(person.displayName(), new_name)
            else:
                print "Successfully changed name"

            # Flush to address book
            self.address_book.save()

    def _change_contact_picture(self, person, picture_path):
        # Backup image data in case something goes wrong
        image_data_backup = person.imageData()

        python_image_data = open(picture_path, "rb").read()
        objc_image_data = AddressBook.NSData.alloc().initWithBytes_length_(python_image_data, len(python_image_data))

        if person.setImageData_(objc_image_data):
            print "Success setting picture!"
            self._add_to_cache(picture_path)
        else:
            print "Failed setting picture... Trying to restore"
            if person.setImageData_(image_data_backup):
                print "Restored successfully"
            else:
                print "Restore failed. Sorry"

        # Flush to address book
        # TODO: Don't save if failed setting image?
        self.address_book.save()

    def set_contact_pic(self, person_identifier, contact_name, pic_path, offer_change_name=False):
        if pic_path in self.cache:
            print "Skipping {} because already set it's picture in previous run".format(contact_name)
            return

        # First try to see if this facebook profile was bound to an addressbook entry
        p = self._get_person_from_bindings(person_identifier)

        if p is None:
            matching_people = self._find_matching_people_by_name(contact_name)
            
            while len(matching_people) == 0:
                print "Failed finding {}".format(contact_name)
                different_name = raw_input("If you'd like to search for this contact with a different name, type it: ")
                if len(different_name) == 0:
                    return
                else:
                    offer_change_name = True
                    matching_people = self._find_matching_people_by_name(different_name)
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

            self.bindings[person_identifier] = p.uniqueId()
            self._save_bindings()

        print "Found {}".format(contact_name)
        
        if offer_change_name:
            self._change_contact_name(p, contact_name)
        
        self._change_contact_picture(p, pic_path)
