DEFAULT_MASK_PHOTO = u'images/default_mask/default.jpg'

BASE_PROFILE = {
        u'attached_to': u'Some Name',
        u'birthday': u'01-01',
        u'career_goals': u'Web Development',
        u'class_of': u'2020',
        u'class_standing': u'Senior',
        u'department': u'None',
        u'email': u'armanda.Woolston@wallawalla.edu',
        u'favorite_books': u'Clean Architecture',
        u'favorite_food': u'Byte size snacks',
        u'favorite_movies': u'Some Movie',
        u'favorite_music': u'Some Music',
        u'gender': u'Other',
        u'graduate': u'No',
        u'high_school': u'SomePlace High',
        u'hobbies': u'Test Driven Development',
        u'majors': u'Computer Science',
        u'minors': u'Web Design and Development',
        u'office': u'None',
        u'office_hours': u'None',
        u'personality': u'ABCD',
        u'pet_peeves': u'Broken Code',
        u'phone': u'111-111-1111',
        u'photo': DEFAULT_MASK_PHOTO,
        u'preprofessional': u'No',
        u'privacy': u'1',
        u'quote': u'A looooooooooooooooooooooooooooooooooooooooooooooooo'
                  u'ooooooooooooooooooooooooooooonnnnnnnnnnnnnnnnnnnnnnn'
                  u'nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnngg'
                  u'ggggggggggggggggggggggg string of text with some wei'
                  u'rd chars !@#$%&amp;*()_+-=`~?&gt;&lt;|}{\\][\';": an'
                  u'd a second " plus a newline\n\nand a\t tab',
        u'quote_author': u'Stephen Ermshar',
        u'relationship_status': u'In engineering...',
        u'website': u'aswwu.com',
    }

# fields that should be visible regardless of the viewer's status
BASE_FIELDS = {
    "email",  # email is visible to not logged in users for individuals with privacy==0, but not for privacy==1, yikes..
    "full_name",
    "photo",
    "username",
    "views",
}

# fields that should only be visible to logged out users if the profile's privacy is "1"
IMPERSONAL_FIELDS = {
    'career_goals',
    'department',
    'favorite_books',
    'favorite_movies',
    'favorite_music',
    'gender',
    'graduate',
    'hobbies',
    'majors',
    'minors',
    'office',
    'office_hours',
    'personality',
    'pet_peeves',
    'preprofessional',
    'privacy',
    'quote',
    'quote_author',
    'relationship_status',
    'website',
}

# fields that should only be visible to logged in users
PERSONAL_FIELDS = {
    'attached_to',
    'birthday',
    'class_of',
    'class_standing',
    'high_school',
    'phone',
}

# fields that should only be visible to a profile's owner
SELF_FIELDS = {
    "wwuid",
    "favorite_food",  # change this, these regression tests are being written for current behavior, not desired
}