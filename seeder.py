from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from item_catalog_set_up import Category, Base, Item, User

engine = create_engine('sqlite:///items_catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

User1 = User(name="Misha", email="misha@udacity.com",picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()
# item catalog
ctegory1 = Category(user_id=1, name="iMac")

session.add(ctegory1)
session.commit()

item1_1 = Item(user_id=1, name="iMac Pro", description="Completely remade for pro users, iMac Pro features the most powerful graphics, processors, storage, memory, and I/O of any Mac.", category=ctegory1)
session.add(item1_1)
session.commit()


item1_2 = Item(user_id=1, name="iMac", description="iMac packs a remarkably powerful computer and the best Mac Retina display ever into an ultrathin design.",category=ctegory1)


session.add(item1_2)
session.commit()



ctegory2 = Category(user_id=1,name="Mac mini")

session.add(ctegory2)
session.commit()

item2_1 = Item(user_id=1,name="Mac mini", description="Now with eighth-generation 6-core and quad-core processors, all-flash storage up to 2TB, and faster 2666MHz DDR4 upgradable memory.",
                      category=ctegory2)
session.add(item2_1)
session.commit()





ctegory3 = Category(user_id=1, name="iPhone")

session.add(ctegory3)
session.commit()

item3_1 = Item(user_id=1, name="iPhoneXR", description="iPhone XR features the new, all-screen Liquid Retina display. Advanced Face ID. The TrueDepth camera. And the new A12 Bionic chip.",category=ctegory3)
session.add(item3_1)
session.commit()


item3_2 = Item(user_id=1, name="iPhoneXS", description="iPhone XS features an all-screen Super Retina display in two sizes. Dual-lens camera system. Face ID. And the new A12 Bionic chip.", category=ctegory3)
session.add(item3_2)
session.commit()


item3_3 = Item(user_id=1, name="iPhoneXS", description="iPhone 8 features a durable glass design. More advanced cameras. The powerful A11 Bionic chip. And wireless charging.", category=ctegory3)
session.add(item3_3)
session.commit()



ctegory4 = Category(user_id=1, name="iPad")

session.add(ctegory4)
session.commit()

item4_1 = Item(user_id=1, name="iPad mini 4", description="Its thinner and lighter than ever before, yet powerfully packed with the fast A8 chip.",  category=ctegory4)
session.add(item4_1)
session.commit()


item4_2 = Item(user_id=1, name="iPad Pro", description="The new iPad Pro features an all-screen design, Liquid Retina display, A12X Bionic chip, Face ID, and is the thinnest iPad ever.", category=ctegory4)
session.add(item4_2)
session.commit()



item4_3 = Item(user_id=1, name="iPad", description="The iPad features a powerful A10 Fusion chip, a gold finish, and support for Apple Pencil.", category=ctegory4)
session.add(item4_3)
session.commit()










ctegory5 = Category(user_id=1, name="Macbook")

session.add(ctegory5)
session.commit()

item5_1 = Item(user_id=1, name="MacBook Pro", description="Thin, light, and available with the revolutionary Touch Bar, the new MacBook Pro is our most powerful notebook ever.", category=ctegory5)
session.add(item5_1)
session.commit()


item5_2 = Item(user_id=1, name="MacBook Air", description="MacBook Air features a Retina display, Touch ID, and a third-generation butterfly keyboard with Force Touch trackpad.", category=ctegory5)
session.add(item5_2)
session.commit()







ctegory7 = Category(user_id=1, name="Apple Watch")

session.add(ctegory7)
session.commit()

item7_1 = Item(user_id=1, name="Apple Watch Series 4", description=" Apple Watch Series 4 features the largest display yet, a new digital crown, low-heart-rate alerts, competitions, and new workouts.", category=ctegory7)
session.add(item7_1)
session.commit()


item7_2 = Item(user_id=1, name="Apple Watch Series 3", description="Apple Watch Series 3. Featuring built-in GPS and altimeter. Smarter coaching in the Activity app. And a remastered Music experience.",category=ctegory7)
session.add(item7_2)
session.commit()


print "added items!"
