#https://github.com/mobolic/facebook-sdk/blob/master/examples/get_posts.py
import AddressBook as ab
address_book = ab.ABAddressBook.sharedAddressBook()
people = address_book.people()

def set_contact_pic(contact_name, pic_path):
    for p in people:
        if p.displayName() != contact_name:
            continue
        
        print "Found {}".format(contact_name)
        
        print "Backing up image data"
        previous_image_data = p.imageData()

        dd = open(pic_path, "rb").read()
        d = ab.NSData.alloc().initWithBytes_length_(dd, len(dd))

        if p.setImageData_(d):
            print "Success setting picture!"
        else:
            print "Failed setting picture... Trying to restore"
            if p.setImageData_(previous_image_data):
                print "Restored successfully"
            else:
                print "Restore failed. Sorry"
        return
    print "Failed finding {}".format(contact_name)
