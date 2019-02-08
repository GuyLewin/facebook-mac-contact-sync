import set_contact_pic
import csv
import os

def main():
    r = csv.reader(open("All Friends.txt", "rb"), delimiter=',', quotechar='"')
    for facebook_profile_url, display_name, contact_pic in r:
        if display_name == "None" or contact_pic == "None":
            print "Invalid contact {} ({}). Skipping".format(facebook_profile_url, display_name)
            continue

        contact_pic_path = os.path.join("Friend's Photos", contact_pic)
        set_contact_pic.set_contact_pic(facebook_profile_url, display_name, contact_pic_path)

if __name__ == "__main__":
    main()
