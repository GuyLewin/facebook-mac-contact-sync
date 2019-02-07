import set_contact_pic
import csv
import os

def main():
    r = csv.reader(open("All Friends.txt", "rb"), delimiter=',', quotechar='"')
    for l in r:
        display_name = l[1]
        contact_pic = l[2]
        if display_name == "None" or contact_pic == "None":
            print "Invalid contact {}. Skipping".format(l)
            continue

        contact_pic_path = os.path.join("Friend's Photos", contact_pic)
        set_contact_pic.set_contact_pic(display_name, contact_pic_path)

if __name__ == "__main__":
    main()