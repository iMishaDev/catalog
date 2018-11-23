# Item Catalog Web App
This web app is a project for the Udacity [FSND Course](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004).

## About
a RESTful web application using the Python framework Flask along with implementing third-party OAuth authentication.

- Efficiently interacting with data is the backbone upon which performant web applications are built
- Properly implementing authentication mechanisms and appropriately mapping HTTP methods to CRUD operations are core features of a properly secured web application

## Acquired Skills:
1. Python
2. HTML
3. CSS
4. OAuth
5. Flask Framework

## Setup
There are some dependancies and a few instructions on how to run the application.
Seperate instructions are provided to get GConnect working also.

## Dependencies
- [Vagrant](https://www.vagrantup.com/)
- [Udacity Vagrantfile](https://github.com/udacity/fullstack-nanodegree-vm)
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads)

## How to Install
1. Install [Vagrant](https://www.vagrantup.com/) & [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
2. Clone the Udacity virtual machine [Virtual Machine](https://github.com/udacity/fullstack-nanodegree-vm)
3. Clone this repository
3. Launch the Vagrant VM (`vagrant up`)
4. Log into Vagrant VM (`vagrant ssh`)
5. Navigate to `cd/vagrant` as instructed in terminal
6. run `sudo pip install requests`
7. Setup application database `python item_catalog_set_up.py`
8. seed the database  `python seeder.py`
9. Run application using `python main.py`
10. open up the browser to http://localhost:5000

## JSON Endpoints
The following are open to the public:

Catalog JSON: `/catalog/JSON`
    - lists all categories in the app.

Categories JSON: `/category/<int:category_id>/items/JSON`
    - lists specific category items.

Category Items JSON: `/category/<int:category_id>/items/JSON`
    - Lists specific category items list.

Category Item JSON: `/category/<int:category_id>/items/<int:item_id>/JSON`
    - Lists specific category item details.
